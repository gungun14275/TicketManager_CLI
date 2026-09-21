# 🎫 Help Desk / IT Ticket Management System

A command-line application for creating, tracking, and resolving IT support tickets — built in Python using Object-Oriented Programming, with local JSON-based data persistence.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-success)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Overview

This project simulates a basic help desk system where support tickets can be created, assigned to staff, tracked through their lifecycle, searched, sorted, and closed — all from a simple terminal menu. Every ticket keeps a full history log, and all data is saved locally so nothing is lost between sessions.

It was built as a hands-on way to practice core Python concepts before moving on to database-backed applications.

---

## ✨ Features

| Feature                  | Description                                                        |
|---------------------------|---------------------------------------------------------------------|
| 🆕 Create ticket          | Log a new issue with a title, description, and priority             |
| 👤 Assign ticket          | Assign (or reassign) a ticket to a support staff member             |
| 🚦 Priority levels        | Low · Medium · High · Critical                                      |
| 📊 Status tracking        | Open · In Progress · Resolved · Closed                              |
| 🔍 Search tickets         | Search by keyword, status, and/or priority                          |
| ↕️ Sort tickets           | Sort by priority or creation date, ascending or descending          |
| ✏️ Update / close ticket  | Change a ticket's status at any point in its lifecycle              |
| 🕘 Ticket history         | Full timestamped log of every change made to a ticket               |
| 📈 Generate summary       | Report showing ticket counts by status and by priority              |
| ✅ Input validation       | Custom exceptions catch invalid priorities, statuses, and empty input |
| 💾 Local data storage     | All tickets are saved to and loaded from a local JSON file          |

---

## 🖥️ Demo

<img src="screenshots/demo.png" alt="CLI demo" width="500"/>

*Closing a ticket and returning to the main menu.*

---

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- No external libraries required — built entirely with the Python standard library

### Installation & Usage

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/ticket-management-system.git
cd ticket-management-system

# 2. Run the program
python3 ticket_system.py
```

On first run, a `tickets_data.json` file will be created automatically in the project folder to store your tickets. On every subsequent run, existing tickets are loaded back in.

---

## 📂 Project Structure

```
ticket-management-system/
│
├── ticket_system.py      # Main application (Ticket, TicketManager, CLI menu)
├── tickets_data.json      # Auto-generated local data file (ignored by git)
├── README.md               # Project documentation
└── screenshots/            # Demo images used in this README
```

---

## 🧠 Concepts Practiced

This project was built to apply the following concepts in order:

```
Python → OOP → Lists/Dictionaries → Sorting/Searching → Functions → Exceptions → File Handling
```

| Concept              | Where it's used                                                  |
|-----------------------|-------------------------------------------------------------------|
| **OOP**               | `Ticket` and `TicketManager` classes separate data from logic     |
| **Lists / Dictionaries** | Tickets stored in a dict keyed by ID; history stored as a list |
| **Sorting / Searching** | `sort_tickets()` and `search_tickets()` methods                 |
| **Functions**         | Every operation (create, assign, update, etc.) is its own method  |
| **Exceptions**        | Custom exception classes (`ValidationError`, `TicketNotFoundError`, etc.) |
| **File Handling**     | `save_to_file()` / `load_from_file()` using the `json` module     |

---

## 🔮 Planned Improvement: Migrating to SQL

The current version stores data in a JSON file. A natural next step is to replace this with **SQLite**, since `TicketManager`'s public methods (`create_ticket`, `search_tickets`, etc.) stay the same regardless of storage engine — only the internals change to use SQL queries instead of JSON read/writes. This keeps the CLI menu code untouched when the storage layer is upgraded.

---

## 🖼️ Adding a Screenshot

1. Run the program and take a screenshot of the menu / a sample operation.
2. Save it as `screenshots/demo.png` in the project folder.
3. Commit and push:
   ```bash
   git add screenshots/demo.png
   git commit -m "Add demo screenshot"
   git push
   ```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Gungun Raj Sah**
BSc IT Student, Ranchi Women's College
