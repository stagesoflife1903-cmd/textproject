"""Translate YouTube comments to English with M2M100 and validate FLORES-101.

Run a non-destructive preflight first:
    python src/translation.py --check-only

Set HF_TOKEN only if the preflight says the model is gated/private, or if a
download receives HTTP 401/403. Never put a token directly in this file.
"""

import argparse
import os
import re
import tarfile
from pathlib import Path

import pandas as pd
import torch
from huggingface_hub import HfApi, get_token
from tqdm import tqdm
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


PROJECT_DIR = Path(__file__).resolve().parents[1]
MODEL_NAME = "facebook/m2m100_418M"
TARGET_LANG = "en"

# M2M100 accepts ISO-639-1 codes. The CSV already uses these except Chinese,
# whose two regional labels must be normalised to M2M100's single `zh` code.
LANGUAGE_TO_M2M = {"zh-cn": "zh", "zh-tw": "zh"}

# FLORES-101 names source files with ISO-639-3 codes, so retain this table only
# to validate that a language from the input has a corresponding FLORES sample.
M2M_TO_FLORES = {
    "af": "afr", "ar": "ara", "bg": "bul", "bn": "ben", "ca": "cat",
    "cs": "ces", "cy": "cym", "da": "dan", "de": "deu", "el": "ell",
    "en": "eng", "es": "spa", "et": "est", "fa": "fas", "fi": "fin",
    "fr": "fra", "gu": "guj", "he": "heb", "hi": "hin", "hr": "hrv",
    "hu": "hun", "id": "ind", "it": "ita", "ja": "jpn", "kn": "kan",
    "ko": "kor", "lt": "lit", "lv": "lav", "mk": "mkd", "ml": "mal",
    "mr": "mar", "ne": "npi", "nl": "nld", "no": "nor", "pa": "pan",
    "pl": "pol", "pt": "por", "ro": "ron", "ru": "rus", "sk": "slk",
    "sl": "slv", "so": "som", "sq": "sqi", "sv": "swe", "sw": "swh",
    "ta": "tam", "te": "tel", "th": "tha", "tl": "tgl", "tr": "tur",
    "uk": "ukr", "ur": "urd", "vi": "vie", "zh": "zho",
}


def find_data_file(filename: str) -> Path:
    """Find data in conventional data/ or the repository's existing data,/ directory."""
    candidates = [PROJECT_DIR / "data" / filename,
                  PROJECT_DIR / "data," / filename]
    for candidate in candidates:
        if candidate.is_file():
            print(f"Found {filename}: {candidate}")
            return candidate
    searched = "\n  - ".join(str(path) for path in candidates)
    raise FileNotFoundError(
        f"Cannot find {filename}. Searched:\n  - {searched}")


def flores_language_codes(archive_path: Path) -> set[str]:
    """Return ISO-639-3 source codes listed in FLORES-101 dev/devtest files."""
    pattern = re.compile(
        r"/(?:dev|devtest)/([a-z]{3})(?:_[a-z]+)?\.(?:dev|devtest)$")
    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            codes = {
                match.group(1) for name in archive.getnames()
                if (match := pattern.search(name))
            }
    except (tarfile.TarError, OSError) as error:
        raise RuntimeError(
            f"FLORES archive is unreadable: {archive_path}") from error
    if not codes:
        raise RuntimeError(
            "No FLORES language files were found in the archive.")
    print(
        f"FLORES-101 archive is valid; found {len(codes)} ISO-639-3 language codes.")
    return codes


def check_huggingface_access() -> str | None:
    """Check model visibility without exposing or persisting an authentication token."""
    token = os.getenv("HF_TOKEN") or get_token()
    try:
        info = HfApi().model_info(MODEL_NAME, token=token)
    except Exception as error:
        print(
            f"Cannot verify Hugging Face access: {type(error).__name__}: {error}")
        print("If this is HTTP 401/403, create a read token and set HF_TOKEN.")
        return token

    if getattr(info, "gated", False) or getattr(info, "private", False):
        if not token:
            raise RuntimeError(
                "This model requires authentication. Create a read token, accept any "
                "model access conditions, then set HF_TOKEN before running."
            )
        print("Hugging Face token found; it will be used for this restricted model.")
    elif token:
        print("Hugging Face access verified. A token is available but not required for this public model.")
    else:
        print("Hugging Face access verified. This public model does not require a token.")
    return token


def load_m2m100(token: str | None):
    """Download/load M2M100, passing a token only when the user configured one."""
    options = {"token": token} if token else {}
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, **options)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, **options)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()
    print(f"Loaded {MODEL_NAME} on {device}.")
    return tokenizer, model, device


def supports_m2m_language(tokenizer, language: str | None) -> bool:
    """Use M2M100's stable public API; do not rely on lang_code_to_id."""
    if language is None or pd.isna(language) or language == "":
        return False
    try:
        tokenizer.get_lang_id(language)
    except (KeyError, ValueError):
        return False
    return True


def translate_batch(tokenizer, model, device, texts, source_lang: str) -> list[str]:
    tokenizer.src_lang = source_lang
    inputs = tokenizer(texts, return_tensors="pt", padding=True,
                       truncation=True, max_length=512).to(device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.get_lang_id(TARGET_LANG),
            max_new_tokens=256,
        )
    return tokenizer.batch_decode(output, skip_special_tokens=True)


def main(check_only: bool = False) -> None:
    dataset_path = find_data_file("youtube_comments.csv")
    flores_path = find_data_file("flores101_dataset.tar.gz")
    output_dir = dataset_path.parent
    checkpoint_path = output_dir / "youtube_comments_checkpoint.csv"
    output_path = output_dir / "youtube_comments_translated.csv"

    flores_codes = flores_language_codes(flores_path)
    hf_token = check_huggingface_access()
    if check_only:
        print("Preflight complete: no model was downloaded and no CSV was changed.")
        return

    tokenizer, model, device = load_m2m100(hf_token)
    if checkpoint_path.exists():
        comments = pd.read_csv(checkpoint_path)
        print("Existing checkpoint loaded.")
    else:
        comments = pd.read_csv(dataset_path)
        print(f"Dataset loaded: {len(comments)} rows")

    missing = {"comment_text", "language"}.difference(comments.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    comments["language_normalized"] = comments["language"].astype(
        "string").str.strip().str.lower()
    comments["m2m_code"] = comments["language_normalized"].replace(
        LANGUAGE_TO_M2M)
    comments["flores_code"] = comments["m2m_code"].map(M2M_TO_FLORES)
    comments["is_supported"] = (
        comments["m2m_code"].map(
            lambda code: supports_m2m_language(tokenizer, code))
        & comments["flores_code"].isin(flores_codes)
    )
    print("Unsupported source labels:")
    print(comments.loc[~comments["is_supported"],
          "language"].value_counts(dropna=False))

    if "translated_comment" not in comments:
        comments["translated_comment"] = ""
    else:
        comments["translated_comment"] = comments["translated_comment"].fillna(
            "")
    if "translation_status" not in comments:
        comments["translation_status"] = "pending"
    else:
        comments["translation_status"] = comments["translation_status"].fillna(
            "pending")
    valid_text = comments["comment_text"].notna(
    ) & comments["comment_text"].astype(str).str.strip().ne("")
    english = valid_text & comments["m2m_code"].eq(TARGET_LANG)
    comments.loc[english,
                 "translated_comment"] = comments.loc[english, "comment_text"]
    comments.loc[english, "translation_status"] = "already_english"
    comments.loc[valid_text & ~comments["is_supported"],
                 "translation_status"] = "unsupported"

    todo = (
        valid_text & comments["is_supported"] & ~comments["m2m_code"].eq(
            TARGET_LANG)
        & ~comments["translation_status"].eq("completed")
    )
    batch_size = 4 if device.type == "cpu" else 16
    for source_lang, group in comments.loc[todo].groupby("m2m_code"):
        indices = group.index.tolist()
        for start in tqdm(range(0, len(indices), batch_size), desc=f"Translating {source_lang}"):
            batch_indices = indices[start:start + batch_size]
            try:
                texts = comments.loc[batch_indices,
                                     "comment_text"].astype(str).tolist()
                comments.loc[batch_indices, "translated_comment"] = translate_batch(
                    tokenizer, model, device, texts, source_lang)
                comments.loc[batch_indices, "translation_status"] = "completed"
            except Exception as error:
                print(f"Translation error for {source_lang}: {error}")
                comments.loc[batch_indices, "translation_status"] = "failed"
            comments.to_csv(checkpoint_path, index=False, encoding="utf-8-sig")

    temp_path = checkpoint_path.with_suffix(".tmp")

    comments.to_csv(output_path, index=False, encoding="utf-8-sig")
    print("\nTranslation summary:")
    print(comments["translation_status"].value_counts(dropna=False))
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true",
                        help="Validate FLORES and Hugging Face access only.")
    main(check_only=parser.parse_args().check_only)
