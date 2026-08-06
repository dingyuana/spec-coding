from __future__ import annotations

import csv, io
import logging
import tempfile
from datetime import datetime, timezone
import os

from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.core.auth.deps import get_current_payload, get_current_student, get_current_admin, get_current_counselor
from src.core.auth.utils import create_access_token, hash_password, verify_password, _exchange_code
from src.models.student import Student
from src.models.counselor import Counselor
from src.models.admin import Admin
from src.models.audit_log import AuditLog
from src.schemas.registration import RegistrationCreate
from src.services.registration import create_registration, get_by_openid, update_registration
from src.services.admin import get_students, audit_student, get_dashboard, get_logs, add_counselor, init_seed_data
from src.services.counselor_service import get_class_students, audit_student as counselor_audit, get_dashboard as counselor_dashboard
from src.services.map_service import get_nearby_buildings, calc_route, get_building_list
from src.utils.errors import AppException

logging.basicConfig(level=logging.INFO)

# ── SQLite 数据库（每次启动用临时文件，保证 TestClient 隔离）──
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
DB_PATH = f"sqlite:///{_tmp_db.name}"
_engine = create_engine(DB_PATH)
SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
Base.metadata.create_all(_engine)
init_seed_data(SessionLocal())


def _db():
    return SessionLocal()


app = FastAPI(title="大学新生报到系统", version="1.0.0")


@app.exception_handler(AppException)
def _app_exc_handler(request, exc: AppException):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)


@app.get("/")
def root():
    return {"app": "colldege-spec"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ── 认证 ──────────────────────────────────────────────────
@app.post("/auth/student")
def student_login(body: dict):
    code = body.get("code")
    if not code or len(code) < 4:
        raise HTTPException(status_code=401, detail="登录失败")
    result = _exchange_code(code)
    if not result.get("openid"):
        raise HTTPException(status_code=401, detail="登录失败")
    token = create_access_token(sub=result["openid"], role="student")
    return {"token": token, "expires_in": 86400}


@app.post("/auth/admin")
def admin_login(body: dict):
    db = _db()
    try:
        admin = db.get(Admin, 1)
        if not admin or not verify_password(body.get("password"), admin.password_hash):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        token = create_access_token(sub=str(admin.id), role="admin")
        return {"token": token, "expires_in": 86400}
    finally:
        db.close()


@app.post("/auth/counselor")
def counselor_login(body: dict):
    db = _db()
    try:
        c = Counselor.find_by_username(db, body.get("username"))
        if not c or not verify_password(body.get("password"), c.password_hash):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        token = create_access_token(
            sub=str(c.id), role="counselor",
            class_name=c.class_name, college=c.college,
        )
        return {"token": token, "expires_in": 86400}
    finally:
        db.close()


# ── 学生端 ───────────────────────────────────────────────
@app.post("/student/registration", status_code=201)
def create_reg(body: RegistrationCreate, payload: dict = Depends(get_current_student)):
    db = _db()
    try:
        s = create_registration(db, body, payload["sub"])
    except AppException as e:
        db.close()
        raise HTTPException(status_code=e.status_code, detail=e.message)
    finally:
        db.close()
    return {
        "id": s.id, "openid": s.openid, "student_id": s.student_id,
        "name": s.name, "college": s.college, "class_name": s.class_name,
        "building": s.building, "phone": s.phone,
        "emergency_contact": s.emergency_contact, "emergency_phone": s.emergency_phone,
        "enrollment_date": str(s.enrollment_date), "status": s.status,
        "reject_reason": s.reject_reason,
    }


@app.get("/student/registration")
def get_reg(payload: dict = Depends(get_current_student)):
    db = _db()
    s = get_by_openid(db, payload["sub"])
    db.close()
    if not s:
        raise HTTPException(status_code=404, detail="未提交")
    return {
        "id": s.id, "openid": s.openid, "student_id": s.student_id,
        "name": s.name, "college": s.college, "class_name": s.class_name,
        "building": s.building, "phone": s.phone,
        "emergency_contact": s.emergency_contact, "emergency_phone": s.emergency_phone,
        "enrollment_date": str(s.enrollment_date), "status": s.status,
        "reject_reason": s.reject_reason,
    }


@app.put("/student/registration")
def update_reg(body: RegistrationCreate, payload: dict = Depends(get_current_student)):
    db = _db()
    try:
        s = update_registration(db, body, payload["sub"])
    except AppException as e:
        db.close()
        raise HTTPException(status_code=e.status_code, detail=e.message)
    finally:
        db.close()
    return {
        "id": s.id, "openid": s.openid, "student_id": s.student_id,
        "name": s.name, "college": s.college, "class_name": s.class_name,
        "building": s.building, "phone": s.phone,
        "emergency_contact": s.emergency_contact, "emergency_phone": s.emergency_phone,
        "enrollment_date": str(s.enrollment_date), "status": s.status,
        "reject_reason": s.reject_reason,
    }


# ── 辅导员端 ─────────────────────────────────────────────
@app.get("/counselor/students")
def counselor_students(
    page: int = 1, size: int = 20, status: str = None,
    payload: dict = Depends(get_current_counselor),
):
    db = _db()
    result = get_class_students(db, payload["class_name"], page, size, status)
    db.close()
    return result


@app.post("/counselor/audit/{sid}")
def counselor_audit_route(sid: int, body: dict, payload: dict = Depends(get_current_counselor)):
    db = _db()
    try:
        action = body.get("action")
        reason = body.get("reason")
        counselor_audit(
            db, sid, action, payload["class_name"],
            actor_type="counselor", actor_name="counselor", reason=reason,
        )
        return {"status": action}
    except AppException as e:
        db.close()
        raise HTTPException(status_code=e.status_code, detail=e.message)
    finally:
        db.close()


@app.get("/counselor/dashboard")
def counselor_dash(payload: dict = Depends(get_current_counselor)):
    db = _db()
    result = counselor_dashboard(db, payload["class_name"])
    db.close()
    return result


# ── 管理端 ───────────────────────────────────────────────
@app.get("/admin/students")
def admin_students(
    page: int = 1, size: int = 20, college: str = None,
    class_name: str = None, status: str = None,
    payload: dict = Depends(get_current_admin),
):
    db = _db()
    result = get_students(db, page, size, college, class_name, status)
    db.close()
    return result


@app.post("/admin/audit/{sid}")
def admin_audit_route(sid: int, body: dict, payload: dict = Depends(get_current_admin)):
    db = _db()
    try:
        action = body.get("action")
        reason = body.get("reason")
        audit_student(
            db, sid, action, actor_type="admin",
            actor_id=1, actor_name="admin", reason=reason,
        )
        return {"status": action}
    except AppException as e:
        db.close()
        raise HTTPException(status_code=e.status_code, detail=e.message)
    finally:
        db.close()


@app.get("/admin/export")
def admin_export(payload: dict = Depends(get_current_admin)):
    db = _db()
    students = Student.find_all(db)
    db.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["student_id", "name", "college", "class_name", "phone", "status", "created_at"])
    for s in students:
        writer.writerow([s.student_id, s.name, s.college, s.class_name, s.phone, s.status, str(s.created_at)])
    content = output.getvalue()
    output.close()
    return Response(content=content, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=students.csv"})


@app.get("/admin/dashboard")
def admin_dash(payload: dict = Depends(get_current_admin)):
    db = _db()
    result = get_dashboard(db)
    db.close()
    return result


@app.get("/admin/logs")
def admin_logs(page: int = 1, size: int = 20, action: str = None, payload: dict = Depends(get_current_admin)):
    db = _db()
    result = get_logs(db, page, size, action)
    db.close()
    return result


@app.post("/admin/counselors", status_code=201)
def admin_add_counselor(body: dict, payload: dict = Depends(get_current_admin)):
    db = _db()
    try:
        c = add_counselor(db, body["username"], body["password"], body["name"],
                           body["college"], body["class_name"])
        return {"id": c.id, "username": c.username, "name": c.name}
    except AppException as e:
        db.close()
        raise HTTPException(status_code=e.status_code, detail=e.message)
    finally:
        db.close()


# ── 地图 ─────────────────────────────────────────────────
@app.get("/map/nearby")
def map_nearby(
    lat: float, lng: float, radius: int = 1000,
    payload: dict = Depends(get_current_payload),
):
    return {"buildings": get_nearby_buildings(lat, lng, radius)}


@app.get("/map/route")
def map_route(
    from_lat: float, from_lng: float, to_lat: float, to_lng: float,
    from_name: str = None, to_name: str = None,
    payload: dict = Depends(get_current_payload),
):
    return calc_route(from_lat, from_lng, to_lat, to_lng, from_name, to_name)


@app.get("/map/buildings")
def map_buildings(type: str = None, payload: dict = Depends(get_current_payload)):
    return {"buildings": get_building_list(type)}
