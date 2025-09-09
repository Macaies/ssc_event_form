1. System Flow – Applicant Journey
flowchart TD
    A[Applicant User] --> B[7-Step Wizard Form]
    B --> C[Validation: email, phone, required fields]
    C --> D[Decision Engine]
    D -->|Assessable| E[Marked for Admin Review]
    D -->|Self-Assessable| F[Auto-Approved → Calendar (Public)]

📌 2. Data Flow (Form Submission)
+------------------------+
| Flask Application      |
|------------------------|
| - app.py               |
| - auth.py              |
+------------------------+
            ↓
+------------------------+
| SQLite Database: app.db|
|------------------------|
| Applications Table     |  (all submissions)
| Events Table           |  (approved events)
+------------------------+
            ↓
Frontend Views:
  • calendar.html  → Public FullCalendar (reads Events table)  
  • admin.html     → Admin view (reads Applications table)  

📌 3. System Components
+----------------------------+
| Applicant (Frontend)       |
|  HTML + JS (Wizard Form)   |
+----------------------------+

+----------------------------+
| Flask Web App              |
|----------------------------|
| app.py       → routes, logic
| auth.py      → login/admin
| location.py  → venues API
| form.js      → wizard UI
| location.js  → location picker
+----------------------------+

+----------------------------+
| SQLite Database            |
|----------------------------|
| applications → all submissions
| events       → approved events
| users        → login roles
+----------------------------+

📌 4. Admin Interaction Flow
flowchart TD
    A[Admin User] --> B[Login Page]
    B --> C[Verify Users (SQLite)]
    C --> D[Admin Dashboard]
    D --> E[View Applications (all)]
    D --> F[Review Assessable Submissions]
    D --> G[Monitor Approved Events]

✅ Features

🔹 Multi-step wizard form (applicants)

🔹 Auto-approve Self-Assessable events

🔹 Admin review for Assessable events

🔹 Public calendar integration (FullCalendar.js)

🔹 Role-based login (Applicants / Admin)
