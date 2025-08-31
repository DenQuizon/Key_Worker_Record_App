# Alyson House Key Worker App

A comprehensive desktop application designed for key workers to manage service user records, track health assessments, and generate reports. This application is specifically built for care facilities to streamline documentation and improve care management workflows.

## Features

### 🏠 Service User Management
- Add, edit, and manage service user profiles
- Store personal information including name and date of birth
- Organize records by individual users

### 📋 Monthly Care Forms
- Create and manage monthly assessment forms for each service user
- Comprehensive health and wellness tracking including:
  - Weight and blood pressure monitoring
  - Health concerns documentation
  - Personal care tracking (nails, hair)
  - Medication administration record (MAR) sheets
  - Financial management (cash box, top-up tracking)
  - Shopping requirements assessment
  - Care documentation management
  - Appointment scheduling and tracking
  - Emotional wellbeing indicators with visual icons
  - Family communication logs
  - Goal setting and progress tracking

### 👥 User Management System
- Role-based access control (Staff and Supervisor roles)
- Secure login with password protection
- First-time login password change enforcement
- Activity logging for audit trails

### 📊 Reporting & Documentation
- PDF generation for completed forms
- Activity log viewing for supervisors
- Date-based form organization and retrieval

### 🔧 Administrative Features
- Supervisor-only user management
- Activity monitoring and logging
- Database management utilities
- Executable building capabilities

## Screenshots

## Screenshots

![Login page screenshot] | (https://github.com/DenQuizon/Key_Worker_Record_App/blob/main/KeyWorkerApp/images/Login_Page.png)

## Installation

### Prerequisites
- Python 3.8 or higher
- Required dependencies (see requirements.txt)

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd KeyWorkerApp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Building Executable

The application can be built into a standalone executable using PyInstaller:

```bash
python simple_build.py
```

Or use the provided VS Code tasks for building.

## Usage

### First Time Setup
1. Launch the application
2. Login with the default supervisor account:
   - Username: `supervisor`
   - Password: `password`
3. Change the default password when prompted
4. Add service users through the "Manage Service Users" option
5. Create staff accounts through "Manage App Users" (supervisor only)

### Creating Monthly Forms
1. Select a service user from the dropdown
2. Choose the month and year
3. Click "View / Create Form"
4. Fill out the comprehensive assessment form across multiple tabs
5. Save the form and generate PDF reports as needed

### User Roles
- **Staff**: Can view/create forms, manage service users
- **Supervisor**: Full access including user management and activity logs

## Technical Details

### Technology Stack
- **Frontend**: CustomTkinter (Modern UI library)
- **Database**: SQLite3
- **PDF Generation**: ReportLab
- **Additional Libraries**: PIL/Pillow, pandas, python-docx

### Database Schema
- `users`: Application user accounts and roles
- `service_users`: Care recipients information
- `forms`: Monthly assessment forms
- `appointments`: Appointment tracking
- `activity_log`: System activity audit trail

### File Structure
```
KeyWorkerApp/
├── main.py                          # Main application entry point
├── login_window.py                  # User authentication
├── form_window.py                   # Main form interface
├── user_management_window.py        # Service user management
├── app_user_management_window.py    # App user management
├── activity_log_window.py           # Activity monitoring
├── database.py                      # Database initialization
├── database_utils.py                # Database operations
├── pdf_generator.py                 # PDF report generation
├── alyson_house.db                  # SQLite database
├── requirements.txt                 # Python dependencies
├── app_icon.ico                     # Application icon
└── images/                          # UI icons and images
```

## Configuration

### Database
The application uses SQLite database (`alyson_house.db`) which is automatically created and initialized on first run.

### Default Credentials
- **Username**: supervisor
- **Password**: password (must be changed on first login)

## Development

### Running in Development Mode
```bash
python main.py
```

### Database Management
Utility scripts are provided for database operations:
- `check_users.py` - View current users
- `reset_supervisor_password.py` - Reset supervisor password
- `database_utils.py` - Database helper functions

### Building Distribution
Use the provided build scripts:
- `simple_build.py` - Simple build script
- `AlysonHouseApp.spec` - PyInstaller specification file

## Security Features

- Password hashing using SHA-256
- Role-based access control
- Activity logging for audit compliance
- Forced password changes on first login
- Secure session management

## Requirements

See `requirements.txt` for complete dependency list. Key dependencies include:
- customtkinter >= 5.2.2
- CTkMessagebox >= 2.7
- reportlab >= 4.4.2
- pillow >= 11.2.1
- pandas >= 2.2.3
- python-docx >= 1.1.2

## License

This project is designed for care facility management. Please ensure compliance with relevant data protection regulations (GDPR, HIPAA, etc.) when handling personal and health information.

## Support

For issues, feature requests, or questions:
1. Check the existing issues in this repository
2. Create a new issue with detailed description
3. Include steps to reproduce any bugs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request with detailed description

---

**Note**: This application handles sensitive personal and health information. Ensure proper data protection measures are in place when deploying in production environments.

