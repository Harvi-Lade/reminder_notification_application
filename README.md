# Reminder Notification Application (CLI)  

A professional, feature-rich, and flexible **command-line reminder application** built in Python. This project showcases advanced Python programming skills, including scheduling, database management, multi-channel notifications, and input validation.  

This application allows users to create, manage, and receive reminders via **mobile (Pushbullet), email, and desktop notifications**. It handles recurring reminders (daily, weekly, monthly, yearly), auto-deletes old notifications, and provides a clean and organized view of all reminders.  

---

## 🚀 Key Features  
✅ **Create, Edit, Delete, and View Reminders** – Manage reminders efficiently through an intuitive CLI interface.  
✅ **Advanced Scheduling and Recurrence** – Supports `None`, `Daily`, `Weekly`, `Monthly`, and `Yearly` recurrence patterns.  
✅ **Smart Notifications** – Get notified via:  
   - **Pushbullet** – Mobile notifications.  
   - **Email** – Personalized email alerts.  
   - **Desktop** – Local system notifications.  
✅ **Upcoming and Due Reminders** – Fetches reminders that are due or scheduled to occur soon.  
✅ **Auto Cleanup** – Old notified reminders with recurrence as 'none' are automatically deleted after 7 days.  
✅ **Flexible Display** – View reminders:  
   - **Date-wise**  
   - **Month-wise**  
   - **Year-wise**  
   - **All at once**  
✅ **Unique Reminder Titles** – Each reminder requires a distinct title for easy identification.  
✅ **Robust Input Validation** – Ensures proper format and prevents incorrect data entry.  
✅ **Better Error Handling** – Catches and manages errors gracefully, improving user experience.  

---

## 🌟 Why This Project Stands Out  
🔥 **Pushbullet Integration** – Get real-time notifications directly on your phone.  
🔥 **Smart Recurrence Handling** – Automatically calculates and manages next occurrences.  
🔥 **Email Notifications** – Stay updated with timely email alerts.  
🔥 **Clean and Organized CLI** – Intuitive and easy-to-use interface.  

---

## 💡 Skills & Technologies  
### **Core Technologies:**  
- **Python** – Core programming language  
- **SQLite** – Lightweight database for data storage  
- **Pushbullet API** – For real-time mobile notifications  
- **Email (SMTP)** – For email-based alerts  
- **CLI (Command-Line Interface)** – For user interaction  
- **Scheduling and Recurrence** – For automated event handling  
- **Error Handling** – For increased stability and reliability  
- **Input Validation** – For ensuring data integrity and consistency  

### **Development Tools:**  
- **Git** – For version control and code management  
- **PyCharm** – For developing and debugging  

---

## 🛠️ Modules Used  
| Module         | Purpose                                                                 |
|---------------|----------------------------------------------------------------------------|
| `calendar`     | Date-based recurrence calculations                                        |
| `datetime`     | Date and time manipulation                                                 |
| `json`         | Storing and reading configuration settings                                 |
| `smtplib`      | Sending email notifications                                                |
| `requests`     | Handling Pushbullet API requests                                           |
| `email`        | Formatting and sending email content                                       |
| `plyer`        | Desktop notifications                                                      |
| `re`           | Regular expressions for input validation                                   |
| `logging`      | Improved error handling and debugging                                      |
| **Type Hints** | Code readability and maintainability                                        |

---

## 🏗️ Project Structure  
The project follows a clean and organized structure for better scalability and maintainability:  
```
reminder_notification_application/
├── config/
│   └── settings.py             # Configuration settings (DB path, email, API keys)
├── database/
│   └── db_manager.py           # Database connection and query management
├── services/
│   ├── notification_service.py # Manages desktop, Pushbullet (mobile), and email notifications
│   ├── reminder_manager.py     # Core logic for handling reminders (CRUD)
│   └── scheduler_service.py    # Handles recurrence, due reminders, upcoming reminders
├── utils/
│   └── validation_utils.py     # Input validation
├── views/
│   └── cli_menu.py             # CLI menu and user input handling
├── main.py                     # Entry point of the application
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Installation  
1. **Clone the Repository:**  
```bash
git clone https://github.com/yourusername/reminder_notification_application.git
cd reminder_notification_application
```

2. **Create a Virtual Environment:**  
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows
```

3. **Install Dependencies:**  
```bash
pip install -r requirements.txt
```

4. **Configure Settings:**  
- Add your **Pushbullet API key**, **database name**, **email** (sender), and **password** in `config/settings.py`.  

5. **Run the Application:**  
```bash
python main.py
```

---

## 🧪 Git Commands  
The following Git commands were used to manage the development process and version control:  

| Command | Description |
|---------|-------------|
| `git init` | Initialize a new Git repository |
| `git clone <repo>` | Clone an existing repository |
| `git add .` | Stage all changes for commit |
| `git commit -m "message"` | Commit staged changes |
| `git push origin main` | Push changes to the remote repository |
| `git pull origin main` | Pull latest changes from the remote repository |
| `git branch` | List all branches |
| `git checkout -b <branch>` | Create and switch to a new branch |
| `git merge <branch>` | Merge specified branch into current branch |
| `git log` | Show commit history |

---

## 🎯 Development Environment  
- **IDE:** PyCharm – Used for development and debugging  
- **Git:** Used for version control and tracking changes  
- **Python 3.12.4** – Core language for development  

---

## 🤝 Contributing  
Contributions are welcome! Feel free to open an issue or submit a pull request.  

---

## 📄 License  
This project is currently not under any specific license. For personal use and showcasing only.  

---

## 📬 Contact  
- **[GitHub](https://github.com/Harvi-Lade/reminder_notification_application)**  
- **[LinkedIn](https://www.linkedin.com/in/harvilade2102/)**  

---

🔥 **This project is designed to demonstrate professional Python development skills** — including clean architecture, modular design, and robust scheduling. Impress recruiters and peers with this versatile and well-structured application!
