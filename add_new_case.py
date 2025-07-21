import sqlite3

def add_case(criminal_id, jurisdiction, section, status, date_registered, officer_name):
    try:
        conn = sqlite3.connect("Criminal Tracking System.db")
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO cases (criminal_id, jurisdiction, section_of_law, status, date_registered, officer_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (criminal_id, jurisdiction, section, status, date_registered, officer_name))

        conn.commit()
        return True, f"✅ New case linked to criminal ID {criminal_id}"
    except Exception as e:
        return False, f"⚠️ Failed to add case: {e}"
    finally:
        conn.close()