from datetime import datetime, timedelta
from db import get_conn

payload = [
    {
        "event_type": "community_event",
        "applicant_name": "Alex Lee",
        "applicant_email": "alex@example.com",
        "applicant_phone": "0400 000 000",
        "event_name": "Sunset Yoga",
        "location": "Seaside Park",
        "start_date": (datetime.now()+timedelta(days=7)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now()+timedelta(days=7)).strftime("%Y-%m-%d"),
        "attendance": 80,
        "alcohol": "No",
        "high_risk": "No",
        "traffic_mgmt": "No",
        "vehicle_access": "No",
        "amplified_sound": "No",
        "noise_level": 0,
        "total_days": 1,
        "notes": "Sunset community yoga",
        "classification": "Self-assessable",
        "status": "Pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "event_type": "community_event",
        "applicant_name": "Pat Morgan",
        "applicant_email": "pat@example.com",
        "applicant_phone": "0400 111 111",
        "event_name": "Live Bands on the Lawn",
        "location": "Riverside Reserve",
        "start_date": (datetime.now()+timedelta(days=14)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now()+timedelta(days=14)).strftime("%Y-%m-%d"),
        "attendance": 450,
        "alcohol": "Yes",
        "high_risk": "No",
        "traffic_mgmt": "Yes",
        "vehicle_access": "No",
        "amplified_sound": "Yes",
        "noise_level": 98,
        "total_days": 1,
        "notes": "Amplified music and bar",
        "classification": "Assessable",
        "status": "Pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
]

with get_conn() as conn:
    cur = conn.cursor()
    for row in payload:
        cols = ",".join(row.keys())
        qs = ",".join(["?"]*len(row))
        cur.execute(f"INSERT INTO events ({cols}) VALUES ({qs})", tuple(row.values()))
    conn.commit()
print("Seeded sample events.")
