# GUIDELINE: SETUP HUGGING FACE TOKEN & RUN TRANSLATION.PY

## 1. Mục đích

Tài liệu hướng dẫn các thành viên thiết lập Hugging Face Access Token và chạy file `translation.py` có sẵn trong dự án.

Mục tiêu:
- Xác thực tài khoản Hugging Face.
- Thiết lập môi trường Python.
- Cài đặt các thư viện cần thiết.
- Chạy chương trình dịch dữ liệu bằng file `translation.py`.

**Lưu ý:** Không tự ý chỉnh sửa logic trong `translation.py` nếu chưa được yêu cầu.

## 2. Chuẩn bị

Trước khi thực hiện, cần có:

- Python đã được cài đặt.
- VS Code hoặc một IDE hỗ trợ Python.
- Source code của dự án.
- File `translation.py`.
- File `requirements.txt` (nếu dự án đã cung cấp).

## 3. Tạo Hugging Face Access Token

**Bước 1:** Truy cập:

https://huggingface.co/settings/tokens

**Bước 2:** Đăng nhập tài khoản Hugging Face.

**Bước 3:** Chọn Create new token.

**Bước 4:** Thiết lập:
- Token name: `translation-project`.
- Token type/permission: Read.

**Bước 5:** Nhấn Create token và copy token vừa tạo.

Lưu ý:
- Mỗi thành viên tự tạo token bằng tài khoản cá nhân.
- Không sử dụng chung token.
- Không chia sẻ token cho người khác.
- Nếu mất token, tạo token mới.

## 4. Thiết lập môi trường Python

Mở thư mục dự án bằng VS Code.

Mở Terminal và kiểm tra Python:

```powershell
python --version
```

### 4.1. Tạo virtual environment (nếu chưa có)

```powershell
python -m venv venv
```

### 4.2. Activate virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Nếu activate thành công, Terminal sẽ hiển thị `(venv)` ở đầu dòng lệnh.

### 4.3. Cài đặt dependencies

Nếu dự án có file `requirements.txt`:

```powershell
pip install -r requirements.txt
```

Nếu chưa có file requirements, cần cài đặt các thư viện theo danh sách dependencies được cung cấp riêng cho dự án.

## 5. Đăng nhập Hugging Face

Trong Terminal (đảm bảo đã activate `venv`), chạy:

```powershell
hf auth login
```

Dán Access Token đã tạo ở bước 3 khi được yêu cầu.

Sau đó kiểm tra:

```powershell
hf auth whoami
```

Nếu hiển thị username Hugging Face, xác thực thành công.

Lưu ý: Không dán token trực tiếp vào file `translation.py`.

## 6. Kiểm tra cấu trúc thư mục

Đảm bảo các file cần thiết nằm đúng vị trí theo cấu trúc dự án.

Ví dụ:

```text
translation-project/
│
├── data/
│   └── input.csv
│
├── output/
│
├── translation.py
├── requirements.txt
├── README.md
└── .gitignore
```

Tên và vị trí file dữ liệu cần được đối chiếu với cấu hình thực tế trong `translation.py`.

## 7. Chạy chương trình translation.py

Sau khi hoàn tất các bước trên:

**Bước 1:** Kiểm tra đang ở đúng thư mục dự án.

**Bước 2:** Kiểm tra virtual environment đã được activate.

**Bước 3:** Chạy chương trình:

```powershell
python translation.py
```

**Bước 4:** Theo dõi Terminal để kiểm tra tiến trình dịch.

Không đóng Terminal hoặc tắt chương trình khi pipeline vẫn đang chạy.

Nếu chương trình có hỗ trợ checkpoint, cần giữ nguyên các file checkpoint để có thể tiếp tục xử lý khi bị gián đoạn.

## 8. Troubleshooting

| Lỗi | Hướng xử lý |
|---|---|
| `hf is not recognized` | Kiểm tra cài đặt `huggingface_hub` trong venv |
| `401 Unauthorized` | Kiểm tra lại Access Token |
| `403 Forbidden` | Kiểm tra quyền truy cập model |
| `ModuleNotFoundError` | Cài lại dependencies trong đúng venv |
| `FileNotFoundError` | Kiểm tra đường dẫn dataset |
| `CUDA out of memory` | Kiểm tra cấu hình thiết bị và phương thức chạy model |
| Translation bị gián đoạn | Kiểm tra checkpoint và cơ chế resume của script |


**Sau khi hoàn thành checklist, thành viên có thể chạy `translation.py` để thực hiện quá trình dịch dữ liệu.**
