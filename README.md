# ssc_form
1. System Flow (User Journey)
Applicant User
     |
     v
[7-Step Wizard Form]
     |
     |--> Validation (email, phone, required fields)
     v
[Decision Engine]
   |  \
   |   \
   |    --> Assessable --> Marked for Admin Review
   v
Self-Assessable --> Auto-Approved --> Calendar (Public)

🔹 2. Data Flow
[Applicant Form Submission]
        |
        v
+-------------------------+
|  Flask Application      |
|  - app.py               |
|  - auth.py              |
+-------------------------+
        |
        v
[SQLite Database app.db]
        |
        +--> Applications Table (all submissions)
        +--> Events Table (approved events)
        |
        v
Frontend Views:
- Calendar.html (FullCalendar, reads Events table)
- Admin.html (reads Applications table)

🔹 3. System Components Diagram
         +------------------------+
         |   Applicant (Frontend) |
         | HTML + JS (Wizard)     |
         +-----------+------------+
                     |
                     v
              [Flask Web App]
   +-----------------------------------+
   | app.py (routes, logic)           |
   | auth.py (login/admin)            |
   | location.py (venues API)         |
   | form.js, location.js (wizard, UI)|
   +-----------------------------------+
                     |
                     v
              [SQLite Database]
       +-------------------------------+
       | applications (submissions)    |
       | events (approved for calendar)|
       | users (login roles)           |
       +-------------------------------+

🔹 4. Admin Interaction Flow
Admin User
   |
   v
[Login Page] --> Verify (SQLite: users table)
   |
   v
[Admin Dashboard]
   |
   |--> View Applications (all)
   |--> Review Assessable Submissions
   |--> Monitor Approved Events
