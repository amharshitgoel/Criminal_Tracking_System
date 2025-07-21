import sqlite3

def search_criminal_with_cases(
    query=None,
    section_of_law=None,
    jurisdiction=None,
    gender=None,
    age_range=None
):
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()

    # 🔍 Build base query and filters
    conditions = []
    params = []

    if query:
        # Check Aadhaar exact match
        conditions.append("(aadhaar = ? OR name LIKE ?)")
        params.extend([query, f"%{query}%"])

    if gender:
        conditions.append("gender = ?")
        params.append(gender)

    if section_of_law:
        conditions.append("id IN (SELECT criminal_id FROM cases WHERE section_of_law LIKE ?)")
        params.append(f"%{section_of_law}%")

    if jurisdiction:
        conditions.append("id IN (SELECT criminal_id FROM cases WHERE jurisdiction LIKE ?)")
        params.append(f"%{jurisdiction}%")

    if age_range:
        conditions.append("age BETWEEN ? AND ?")
        params.extend([age_range[0], age_range[1]])

    # Final query
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    cur.execute(f"SELECT * FROM criminals WHERE {where_clause}", tuple(params))
    results = cur.fetchall()

    if not results:
        conn.close()
        return []

    criminal_data = []
    for criminal in results:
        criminal_id = criminal[0]
        photo_blob = criminal[8] if len(criminal) > 8 else None

        # 📂 Fetch related cases
        cur.execute("""
            SELECT jurisdiction, section_of_law, status,
                   date_registered, officer_name
            FROM cases WHERE criminal_id = ?
        """, (criminal_id,))
        cases = cur.fetchall()

        # 📦 Structure for UI
        criminal_info = {
            "id": criminal[0],
            "name": criminal[1],
            "age": criminal[2],
            "mobile": criminal[3],
            "address": criminal[4],
            "dob": criminal[5],
            "aadhaar": criminal[6],
            "gender": criminal[7],
            "photo_blob": photo_blob,
            "cases": cases
        }

        criminal_data.append(criminal_info)

    conn.close()
    return criminal_data