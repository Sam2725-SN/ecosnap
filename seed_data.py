#!/usr/bin/env python3
"""
seed_data.py – Populate EcoSnap database with sample complaints
Run AFTER starting the app once (so tables are created):
    python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.complaint import Complaint, StatusEnum
from app.auth import hash_password
from datetime import datetime, timedelta
import random

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Sample users ───────────────────────────────────────────
users_data = [
    {"name": "Priya Sharma",   "email": "priya@example.com",   "password": "pass123"},
    {"name": "Rahul Verma",    "email": "rahul@example.com",    "password": "pass123"},
    {"name": "Anita Patel",    "email": "anita@example.com",    "password": "pass123"},
    {"name": "Kiran Mehta",    "email": "kiran@example.com",    "password": "pass123"},
]

created_users = []
for ud in users_data:
    existing = db.query(User).filter(User.email == ud["email"]).first()
    if not existing:
        u = User(name=ud["name"], email=ud["email"], hashed_password=hash_password(ud["password"]))
        db.add(u)
        db.flush()
        created_users.append(u)
        print(f"✅ Created user: {ud['email']}")
    else:
        created_users.append(existing)
        print(f"⚠️  User already exists: {ud['email']}")

db.commit()

# ── Sample complaints ──────────────────────────────────────
complaints_data = [
    {"location": "MG Road, Near Bus Stop 12, Bengaluru",     "description": "Large pile of garbage bags left on footpath for 3 days. Strong smell and blocking pedestrian movement.", "status": StatusEnum.resolved},
    {"location": "Koramangala 5th Block, Bengaluru",          "description": "Illegal dumping of construction waste next to a residential building. Has been there for over a week.", "status": StatusEnum.in_progress},
    {"location": "Indiranagar 100 Feet Road, Bengaluru",     "description": "Overflowing municipal dustbin near bakery. Trash spilling onto road and causing traffic hazard.", "status": StatusEnum.pending},
    {"location": "HSR Layout Sector 2, Bengaluru",            "description": "Plastic waste and broken bottles near playground. Children playing nearby could be injured.", "status": StatusEnum.resolved},
    {"location": "Whitefield Main Road, Bengaluru",           "description": "Burning of garbage in open area producing toxic smoke. Residents with asthma are severely affected.", "status": StatusEnum.in_progress},
    {"location": "Jayanagar 4th Block, Bengaluru",            "description": "Electronic waste (old TVs, computers) abandoned on roadside. Leaking harmful materials.", "status": StatusEnum.pending},
    {"location": "BTM Layout 2nd Stage, Bengaluru",           "description": "Garbage dumped in storm water drain, causing blockage and flooding risk during rains.", "status": StatusEnum.pending},
    {"location": "Marathahalli Bridge Road, Bengaluru",       "description": "Dead animal near waste pile not being cleared. Multiple complaints made to BBMP but no action.", "status": StatusEnum.resolved},
    {"location": "Silk Board Junction, Bengaluru",            "description": "Vegetable market waste not being collected since two days. Area is infested with flies and rodents.", "status": StatusEnum.in_progress},
    {"location": "Electronic City Phase 1, Bengaluru",        "description": "Industrial waste bags piled up in public area near residential complex without proper disposal.", "status": StatusEnum.pending},
]

for i, cd in enumerate(complaints_data):
    user = random.choice(created_users)
    days_ago = random.randint(1, 30)
    c = Complaint(
        user_id     = user.id,
        location    = cd["location"],
        description = cd["description"],
        status      = cd["status"],
        created_at  = datetime.utcnow() - timedelta(days=days_ago),
    )
    db.add(c)
    print(f"📋 Added complaint #{i+1}: {cd['location'][:40]}…")

db.commit()
db.close()

print("\n🌿 Seed data loaded successfully!")
print("   Admin login: admin@ecosnap.com / admin123")
print("   User login:  priya@example.com / pass123")
