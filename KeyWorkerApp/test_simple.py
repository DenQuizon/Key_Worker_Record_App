import customtkinter as ctk
import database_utils as db_manager

class SimpleApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Test - Key Worker App")
        self.geometry("400x450")
        self.resizable(False, False)
        
        # Test if we can show a simple window first
        label = ctk.CTkLabel(self, text="Test Window - If you see this, the basic window works!")
        label.pack(pady=20)
        
        login_button = ctk.CTkButton(self, text="Test Login", command=self.test_login)
        login_button.pack(pady=10)
        
        # Show window immediately
        self.deiconify()
        self.lift()
        
    def test_login(self):
        # Test the login function directly
        user_data = db_manager.verify_user("supervisor", "admin123")
        if user_data:
            self.show_success(user_data)
        else:
            self.show_error()
            
    def show_success(self, user_data):
        success_label = ctk.CTkLabel(self, text=f"Login Success: {user_data['username']}")
        success_label.pack(pady=10)
        
    def show_error(self):
        error_label = ctk.CTkLabel(self, text="Login Failed!")
        error_label.pack(pady=10)

if __name__ == "__main__":
    app = SimpleApp()
    app.mainloop()
