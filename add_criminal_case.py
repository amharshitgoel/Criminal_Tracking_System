import sqlite3

def add_criminal_and_case(name, age, dob, mobile, address, aadhaar, gender,
                          photo_blob, jurisdiction, section, status, date_registered, officer_name):
    try:
        conn = sqlite3.connect("Criminal Tracking System.db")
        cur = conn.cursor()

        # 🔍 Check if criminal exists
        cur.execute("SELECT id FROM criminals WHERE aadhaar = ?", (aadhaar,))
        existing = cur.fetchone()

        if existing:
            criminal_id = existing[0]
            cur.execute("""
                UPDATE criminals SET name=?, age=?, dob=?, mobile=?, address=?, gender=?
                WHERE aadhaar=?
            """, (name, age, dob, mobile, address, gender, aadhaar))
            # Optional: only update photo if new one is provided
            if photo_blob:
                cur.execute("UPDATE criminals SET photo_blob=? WHERE aadhaar=?", (photo_blob, aadhaar))
            message = "📝 Criminal info updated."
        else:
            cur.execute("""
                INSERT INTO criminals (name, age, dob, mobile, address, aadhaar, gender, photo_blob)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, age, dob, mobile, address, aadhaar, gender, photo_blob))
            criminal_id = cur.lastrowid
            message = "🆕 New criminal added."

        # 📂 Link case
        cur.execute("""
            INSERT INTO cases (criminal_id, jurisdiction, section_of_law, status, date_registered, officer_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (criminal_id, jurisdiction, section, status, date_registered, officer_name))

        conn.commit()
        return True, message + " ✅ Case linked."
    except Exception as e:
        return False, f"⚠️ Error occurred: {e}"
    finally:
        conn.close()