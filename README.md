# Text Project

A Python-based project for YouTube comment analysis, multilingual comment translation, and cyberbullying-related data exploration.

## 1. Repository Structure

```text
textproject/
├── data/
├── notebook/
│   └── text_analysis.ipynb
├── src/
│   └── translation.py
├── requirements.txt
└── README.md
```

The translation script searches for input files in `data/` or the existing `data,/` directory. Keep the original filenames unchanged unless you also update the Python script.

## 2. Install Required Software

Install:
- [Git](https://git-scm.com/downloads)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Code](https://code.visualstudio.com/)
- VS Code extensions: Python and Jupyter

## 3. Clone the Repository

Open Git Bash:

```bash
git clone https://github.com/stagesoflife1903-cmd/textproject.git
cd textproject
```

To update an existing local repository:

```bash
git pull origin main
```

## 4. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate on Windows Git Bash:

```bash
source .venv/Scripts/activate
```

Activate on PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## 5. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 6. Prepare the Datasets

Required input files:

| File | Purpose |
|---|---|
| `youtube_comments.csv` | YouTube comments for analysis and translation |
| `cyberbullying.csv` | Cyberbullying analysis dataset |
| `flores101_dataset.tar.gz` | FLORES-101 language validation archive |

Place the files in the `data/` directory. If datasets are not included in GitHub, download them from the source provided by the project team.

## 7. Run the Translation Script

Run commands from the project root.

First, validate the required files and Hugging Face access:

```bash
python src/translation.py --check-only
```

Then run translation:

```bash
python src/translation.py
```

The script uses `facebook/m2m100_418M`. The first run downloads the model from Hugging Face. An internet connection and sufficient disk space are required.

The script generates:

- `youtube_comments_checkpoint.csv`: Translation progress checkpoint.
- `youtube_comments_translated.csv`: Final translated dataset.

The source CSV must contain `comment_text` and `language` columns.

### Hugging Face Authentication

Only configure a token if the model or download requires authentication.

Git Bash:

```bash
export HF_TOKEN="your_read_token"
```

PowerShell:

```powershell
$env:HF_TOKEN = "your_read_token"
```

Never commit tokens or credentials to GitHub.

## 8. Run the Analysis Notebook

Start Jupyter from the project root:

```bash
jupyter notebook
```

Open:

```text
notebook/text_analysis.ipynb
```

Alternatively, open the notebook in VS Code and select the `.venv` Python kernel.

If datasets are stored in `data/`, use:

```python
cyberbullying = pd.read_csv("data/cyberbullying.csv")
youtube_comments = pd.read_csv("data/youtube_comments.csv")
```

## 9. Update Data and Push to GitHub

After processing data, inspect changes:

```bash
git status
```

Stage the files you want to share:

```bash
git add README.md src/ notebook/
git add data/youtube_comments_translated.csv
```

If you also want to share an updated source dataset:

```bash
git add data/youtube_comments.csv
```

Commit and push:

```bash
git commit -m "Update translated dataset and analysis"
git pull --rebase origin main
git push origin main
```

Verify the updated files on GitHub.

### Important: Large Datasets

GitHub blocks individual files larger than 100 MB. Use Git LFS or an approved external storage service for large datasets.

Do not upload:
- Virtual environments (`.venv/`, `venv/`)
- Model cache folders
- API tokens or credentials
- Temporary files

## 10. Daily Team Workflow

When starting work:

```bash
git pull origin main
```

Activate the environment:

```bash
source .venv/Scripts/activate
```

Run the Python script or notebook.

When finished:

```bash
git status
git add <files-you-want-to-share>
git commit -m "Describe your changes"
git pull --rebase origin main
git push origin main
```

Resolve any merge conflicts before pushing.
