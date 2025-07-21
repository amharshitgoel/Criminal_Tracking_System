from deepface import DeepFace
import sqlite3
import tempfile
import os

def save_blob_to_temp(blob):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        temp.write(blob)
        temp.flush()
        return temp.name

def verify_faces(temp_path_1, temp_path_2, model="ArcFace"):
    try:
        result = DeepFace.verify(temp_path_1, temp_path_2, model_name=model)
        return result.get("verified", False), result.get("distance"), result.get("threshold")
    except Exception:
        return False, None, None

def search_by_uploaded_photo(uploaded_bytes, model="ArcFace"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as uploaded_temp:
        uploaded_temp.write(uploaded_bytes)
        uploaded_temp.flush()
        uploaded_path = uploaded_temp.name

    matches = []
    conn = sqlite3.connect("Criminal Tracking System.db")
    cur = conn.cursor()

    cur.execute("SELECT id, name, gender, mobile, address, photo_blob FROM criminals")
    for row in cur.fetchall():
        crim_id, name, gender, mobile, address, blob = row
        if blob:
            temp_db_image = save_blob_to_temp(blob)
            is_match, distance, threshold = verify_faces(uploaded_path, temp_db_image, model=model)
            os.remove(temp_db_image)

            if is_match:
                # 🧾 Fetch case details
                cur.execute("""
                    SELECT jurisdiction, section_of_law, status,
                           date_registered, officer_name
                    FROM cases WHERE criminal_id = ?
                """, (crim_id,))
                cases = cur.fetchall()

                matches.append({
                    "id": crim_id,
                    "name": name,
                    "gender": gender,
                    "mobile": mobile,
                    "address": address,
                    "cases": cases
                })

    conn.close()
    os.remove(uploaded_path)

    message = "✅ Match found." if matches else "❌ No match found."
    return matches, message