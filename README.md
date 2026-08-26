# FastAPI Research Group Management System

Hệ thống quản lý đề tài nghiên cứu (Research Project Management) xây dựng bằng **FastAPI**, hỗ trợ quản lý người dùng, đề tài nghiên cứu, thành viên và nhiệm vụ (task) với phân quyền theo vai trò (RBAC).

**Dự án:** IT215_N25DTCN008

---

## 1. Công nghệ sử dụng

- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Database:** SQLite / PostgreSQL
- **Xác thực:** JWT (PyJWT) + Bearer Token
- **Mã hóa mật khẩu:** bcrypt
- **Validation:** Pydantic v2 (`pydantic-settings`)
- **Server:** Uvicorn

---

## 2. Cấu trúc thư mục

```
app/
├── main.py                      # Điểm khởi chạy ứng dụng, khai báo router
├── core/
│   ├── config.py                 # Cấu hình ứng dụng (đọc từ .env)
│   ├── security.py               # Hash mật khẩu, tạo/giải mã JWT
│   └── responses.py              # Chuẩn hoá response (APIResponse)
├── db/
│   └── database.py               # Khởi tạo engine, session SQLAlchemy
├── dependencies/
│   ├── auth.py                   # Dependency lấy user hiện tại từ token
│   └── permissions.py            # Dependency kiểm tra quyền admin
├── models/                       # SQLAlchemy models (bảng dữ liệu)
│   ├── users.py
│   ├── research_projects.py
│   ├── research_members.py
│   └── research_tasks.py
├── schemas/                      # Pydantic schemas (request/response)
│   ├── users.py
│   ├── research_projects.py
│   ├── research_members.py
│   └── research_tasks.py
├── services/                     # Business logic
│   ├── auth_service.py
│   ├── user_service.py
│   ├── research_project_service.py
│   └── research_task_service.py
└── routers/                      # API endpoints
    ├── auth_router.py
    ├── user_router.py
    ├── research_project_router.py
    └── research_task_router.py
```

---

## 3. Cài đặt & Chạy dự án

### 3.1. Yêu cầu

- Python >= 3.10
- pip

### 3.2. Cài đặt môi trường

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Cài đặt thư viện yêu cầu thông qua requirements.txt
pip install -r requirements.txt
```

### 3.3. Cấu hình biến môi trường

Tạo file `.env` ở thư mục gốc:

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> Với PostgreSQL: `DATABASE_URL=postgresql://user:password@localhost:5432/dbname`

### 3.4. Chạy server

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 4. Danh sách API

Base path: `/api/v1`

### Authentication
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/auth/register` | Đăng ký tài khoản mới |
| POST | `/auth/login` | Đăng nhập, nhận `access_token` |

### Users
| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| GET | `/users/me` | Đã đăng nhập | Xem thông tin cá nhân |
| GET | `/users` | ADMIN | Danh sách người dùng (hỗ trợ `search`, `is_active`) |

### Research Projects (Đề tài nghiên cứu)
| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| POST | `/research-projects` | Đã đăng nhập | Tạo đề tài mới (tự động là OWNER) |
| GET | `/research-projects` | Đã đăng nhập | Danh sách đề tài của tôi (hỗ trợ `search`) |
| GET | `/research-projects/{id}` | Owner/Member | Xem chi tiết đề tài |
| PATCH | `/research-projects/{id}` | Owner | Cập nhật đề tài |
| DELETE | `/research-projects/{id}` | Owner | Xóa đề tài |

### Members (Thành viên đề tài)
| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| POST | `/research-projects/{id}/members` | Owner | Thêm thành viên |
| GET | `/research-projects/{id}/members` | Owner/Member | Danh sách thành viên |
| DELETE | `/research-projects/{id}/members/{user_id}` | Owner | Xóa thành viên |

### Research Tasks (Nhiệm vụ nghiên cứu)
| Method | Endpoint | Quyền | Mô tả |
|---|---|---|---|
| POST | `/research-projects/{id}/research-tasks` | Owner/Member | Tạo nhiệm vụ |
| GET | `/research-projects/{id}/research-tasks` | Owner/Member | Danh sách nhiệm vụ (filter, sort, phân trang) |
| GET | `/research-tasks/{id}` | Owner/Member | Xem chi tiết nhiệm vụ |
| PATCH | `/research-tasks/{id}` | Owner (toàn quyền) / Assignee (chỉ status) | Cập nhật nhiệm vụ |
| DELETE | `/research-tasks/{id}` | Owner | Xóa nhiệm vụ |

---

## 5. Phân quyền (RBAC)

| Vai trò | Phạm vi | Quyền hạn |
|---|---|---|
| `ADMIN` (User role) | Toàn hệ thống | Xem danh sách tất cả người dùng |
| `USER` (User role) | Toàn hệ thống | Sử dụng các chức năng thông thường |
| `OWNER` (Member role) | Trong 1 đề tài | Toàn quyền: sửa/xóa đề tài, quản lý thành viên, toàn quyền với task |
| `MEMBER` (Member role) | Trong 1 đề tài | Xem đề tài, tạo task, chỉ sửa `status` của task được giao (assignee) |

**Lưu ý quan trọng:**
- Giá trị enum (`role`, `status`, `priority`) trong toàn bộ hệ thống dùng **chữ thường**: `"owner"`, `"member"`, `"todo"`, `"in_progress"`, `"done"`, `"low"`, `"medium"`, `"high"`.
- Khi tạo member/task, body cần truyền đầy đủ `project_id` (theo schema hiện tại), song song với `id` trên URL path.

---

## 6. Định dạng Response

Toàn bộ API trả về theo cấu trúc chuẩn hoá (`APIResponse`):

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Thông báo kết quả",
  "data": { },
  "errors": null,
  "timestamp": "2026-01-01T00:00:00+00:00",
  "path": "/api/v1/..."
}
```

---

## 7. Kiểm thử API

Dự án có bộ checklist kiểm thử thủ công (`API_Test_Checklist_FastAPI_Research.xlsx`) gồm:
- **API Test Checklist**: 52 test case cho luồng chính, case đúng, case lỗi, validation.
- **Cybersecurity Test Matrix**: 12 test case kiểm thử bảo mật theo OWASP API Security (BOLA, BFLA, Mass Assignment, JWT Security, SQL Injection, Rate Limiting).

Có thể test thủ công qua Swagger UI (`/docs`) hoặc Postman, dùng token JWT lấy từ `/auth/login`, cấu hình ở nút **Authorize** (Swagger) hoặc Header `Authorization: Bearer <token>` (Postman).

---

## 8. Changelog / Các bản sửa lỗi gần đây

- ✅ Validate định dạng email khi đăng ký (`EmailStr` thay vì `str` thường).
- ✅ Bổ sung Rate Limiting cho endpoint `/auth/login` để chống Brute-force.
- ✅ Chuẩn hoá tài liệu Postman/Checklist theo đúng giá trị enum chữ thường mà API thực nhận.
