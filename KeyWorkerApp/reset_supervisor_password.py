import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def reset_supervisor_password():
    con = sqlite3.connect('alyson_house.db')
    cur = con.cursor()
    new_password = 'admin123'
    new_password_hash = hash_password(new_password)
    cur.execute("UPDATE users SET password_hash = ?, first_login = 0 WHERE username = 'supervisor'", (new_password_hash,))
    con.commit()
    con.close()
    print(f"Supervisor password has been reset to '{new_password}'.")

if __name__ == "__main__":
    reset_supervisor_password()
