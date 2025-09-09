⃣ System Flow – User Journey
Applicant User
     ↓
[7-Step Wizard Form]
     ↓
Validation (email, phone, required fields)
     ↓
Decision Engine
     ├─ Assessable → Marked for Admin Review
     └─ Self-Assessable → Auto-Approved → Calendar (Public)



2️⃣ Data Flow
[Applicant Form Submission]
        ↓
+-------------------------+
|  Flask Application      |
|  - app.py               |
|  - auth.py              |
+-------------------------+
        ↓
[SQLite Database: app.db]
        ├─ Applications Table (all submissions)
        ├─ Events Table (approved events)
        ↓
Frontend Views:
- calendar.html (FullCalendar, reads Events table)
- admin.html (reads Applications table)



3️⃣ System Components Diagram
+-----------------------------+
| Applicant (Frontend)       |
| HTML + JS (Wizard Form)    |
+-------------+--------------+
              ↓
       [Flask Web App]
+-----------------------------------+
| app.py         → routes, logic    |
| auth.py        → login/admin      |
| location.py    → venues API       |
| form.js        → wizard UI        |
| location.js    → location picker  |
+-----------------------------------+
              ↓
       [SQLite Database]
+-----------------------------------+
| applications → all submissions    |
| events       → approved events    |
| users        → login roles        |
+-----------------------------------+



4️⃣ Admin Interaction Flow
Admin User
     ↓
[Login Page] → Verify (SQLite: users table)
     ↓
[Admin Dashboard]
     ├─ View Applications (all)
     ├─ Review Assessable Submissions
     └─ Monitor Approved Events




