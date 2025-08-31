import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_users():
    con = sqlite3.connect('alyson_house.db')
    cur = con.cursor()
    cur.execute("SELECT username, password_hash, role, first_login FROM users")
    users = cur.fetchall()
    con.close()
    
    print("Users in database:")
    for username, password_hash, role, first_login in users:
        print(f"Username: {username}")
        print(f"Role: {role}")
        print(f"First Login: {first_login}")
        print(f"Password Hash: {password_hash}")
        
        # Test passwords
        test_passwords = ['password', 'admin123']
        for test_pass in test_passwords:
            if password_hash == hash_password(test_pass):
                print(f"  -> Password is: {test_pass}")
        print("-" * 40)

if __name__ == "__main__":
    check_users()
