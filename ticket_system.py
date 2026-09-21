import json
import os
from datetime import datetime


# --------------------------------------------------------------------
# CUSTOM EXCEPTIONS  (practicing: exceptions)
# --------------------------------------------------------------------
class TicketError(Exception):
    """Base class for all ticket-related errors."""
    pass


class TicketNotFoundError(TicketError):
    """Raised when a ticket ID does not exist."""
    pass


class InvalidPriorityError(TicketError):
    """Raised when an invalid priority level is given."""
    pass


class InvalidStatusError(TicketError):
    """Raised when an invalid status is given."""
    pass


class ValidationError(TicketError):
    """Raised when user input fails validation (e.g. empty title)."""
    pass


# --------------------------------------------------------------------
# CONSTANTS
# --------------------------------------------------------------------
PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]
STATUS_LEVELS = ["Open", "In Progress", "Resolved", "Closed"]
DATA_FILE = "tickets_data.json"


# --------------------------------------------------------------------
# TICKET CLASS  (practicing: OOP)
# --------------------------------------------------------------------
class Ticket:
    """Represents a single help-desk ticket."""

    def __init__(self, ticket_id, title, description, priority,
                 status="Open", assigned_to="Unassigned",
                 created_at=None, updated_at=None, history=None):
        self.ticket_id = ticket_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.assigned_to = assigned_to
        self.created_at = created_at or datetime.now().isoformat(timespec="seconds")
        self.updated_at = updated_at or self.created_at
        # history is a list of dicts -> practicing: lists + dicts together
        self.history = history if history is not None else [
            f"[{self.created_at}] Ticket created with priority '{priority}'."
        ]

    def add_history(self, message):
        """Append a timestamped entry to this ticket's history log."""
        timestamp = datetime.now().isoformat(timespec="seconds")
        self.updated_at = timestamp
        self.history.append(f"[{timestamp}] {message}")

    def to_dict(self):
        """Convert the Ticket object into a plain dict (for JSON saving)."""
        return {
            "ticket_id": self.ticket_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "history": self.history,
        }

    @staticmethod
    def from_dict(data):
        """Rebuild a Ticket object from a dict (loaded from JSON)."""
        return Ticket(
            ticket_id=data["ticket_id"],
            title=data["title"],
            description=data["description"],
            priority=data["priority"],
            status=data["status"],
            assigned_to=data["assigned_to"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            history=data["history"],
        )

    def __str__(self):
        return (f"#{self.ticket_id:<4} | {self.title[:25]:<25} | "
                f"{self.priority:<8} | {self.status:<11} | "
                f"Assigned: {self.assigned_to}")


# --------------------------------------------------------------------
# TICKET MANAGER CLASS  (practicing: OOP, dicts, functions, file I/O)
# --------------------------------------------------------------------
class TicketManager:
    """Owns the collection of tickets and every operation on them."""

    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.tickets = {}          # dict: ticket_id -> Ticket object
        self.next_id = 1
        self.load_from_file()

    # ---------------- validation helpers ----------------
    @staticmethod
    def validate_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field_name} cannot be empty.")
        return value.strip()

    @staticmethod
    def validate_priority(priority):
        priority = priority.strip().title()
        if priority not in PRIORITY_LEVELS:
            raise InvalidPriorityError(
                f"Priority must be one of {PRIORITY_LEVELS}, got '{priority}'."
            )
        return priority

    @staticmethod
    def validate_status(status):
        status = status.strip().title()
        if status not in STATUS_LEVELS:
            raise InvalidStatusError(
                f"Status must be one of {STATUS_LEVELS}, got '{status}'."
            )
        return status

    def _get_ticket_or_raise(self, ticket_id):
        if ticket_id not in self.tickets:
            raise TicketNotFoundError(f"No ticket found with ID #{ticket_id}.")
        return self.tickets[ticket_id]

    # ---------------- core features ----------------
    def create_ticket(self, title, description, priority):
        """Create ticket."""
        title = self.validate_text(title, "Title")
        description = self.validate_text(description, "Description")
        priority = self.validate_priority(priority)

        ticket = Ticket(self.next_id, title, description, priority)
        self.tickets[ticket.ticket_id] = ticket
        self.next_id += 1
        self.save_to_file()
        return ticket

    def assign_ticket(self, ticket_id, assignee):
        """Assign ticket to a support staff member."""
        ticket = self._get_ticket_or_raise(ticket_id)
        assignee = self.validate_text(assignee, "Assignee name")
        old = ticket.assigned_to
        ticket.assigned_to = assignee
        ticket.add_history(f"Reassigned from '{old}' to '{assignee}'.")
        self.save_to_file()
        return ticket

    def update_status(self, ticket_id, new_status):
        """Update/close ticket (status tracking)."""
        ticket = self._get_ticket_or_raise(ticket_id)
        new_status = self.validate_status(new_status)
        old = ticket.status
        ticket.status = new_status
        ticket.add_history(f"Status changed from '{old}' to '{new_status}'.")
        self.save_to_file()
        return ticket

    def close_ticket(self, ticket_id):
        """Convenience wrapper: close a ticket."""
        return self.update_status(ticket_id, "Closed")

    def get_history(self, ticket_id):
        """Ticket history."""
        ticket = self._get_ticket_or_raise(ticket_id)
        return ticket.history

    # ---------------- search & sort (practicing: searching/sorting) ----
    def search_tickets(self, keyword=None, status=None, priority=None):
        """
        Search tickets by keyword (in title/description), and/or filter
        by status and/or priority. Any combination of filters may be used.
        """
        results = list(self.tickets.values())

        if keyword:
            keyword = keyword.lower()
            results = [
                t for t in results
                if keyword in t.title.lower() or keyword in t.description.lower()
            ]
        if status:
            status = self.validate_status(status)
            results = [t for t in results if t.status == status]
        if priority:
            priority = self.validate_priority(priority)
            results = [t for t in results if t.priority == priority]

        return results

    def sort_tickets(self, by="priority", descending=True):
        """
        Sort by priority/date.
        by: "priority" or "date"
        """
        tickets = list(self.tickets.values())

        if by == "priority":
            # Map priority names to a numeric rank so Critical > High > ...
            rank = {level: i for i, level in enumerate(PRIORITY_LEVELS)}
            tickets.sort(key=lambda t: rank[t.priority], reverse=descending)
        elif by == "date":
            tickets.sort(key=lambda t: t.created_at, reverse=descending)
        else:
            raise ValueError("sort_tickets: 'by' must be 'priority' or 'date'.")

        return tickets

    # ---------------- summary report ----------------
    def generate_summary(self):
        """Generate summary: counts by status and by priority."""
        summary = {
            "total_tickets": len(self.tickets),
            "by_status": {s: 0 for s in STATUS_LEVELS},
            "by_priority": {p: 0 for p in PRIORITY_LEVELS},
        }
        for ticket in self.tickets.values():
            summary["by_status"][ticket.status] += 1
            summary["by_priority"][ticket.priority] += 1
        return summary

    # ---------------- file handling (practicing: file I/O) ----------
    def save_to_file(self):
        """Save data locally as JSON."""
        payload = {
            "next_id": self.next_id,
            "tickets": [t.to_dict() for t in self.tickets.values()],
        }
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except OSError as e:
            print(f"[Warning] Could not save data to file: {e}")

    def load_from_file(self):
        """Load previously saved tickets, if the data file exists."""
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            self.next_id = payload.get("next_id", 1)
            for data in payload.get("tickets", []):
                ticket = Ticket.from_dict(data)
                self.tickets[ticket.ticket_id] = ticket
        except (OSError, json.JSONDecodeError) as e:
            print(f"[Warning] Could not load existing data: {e}")


# --------------------------------------------------------------------
# CLI HELPERS
# --------------------------------------------------------------------
def prompt_choice(prompt_text, options):
    """Ask the user to pick from a fixed list of options; re-ask on bad input."""
    options_display = "/".join(options)
    while True:
        value = input(f"{prompt_text} ({options_display}): ").strip()
        for option in options:
            if value.lower() == option.lower():
                return option
        print(f"  Please enter one of: {options_display}")


def print_ticket_table(tickets):
    if not tickets:
        print("  No tickets to show.")
        return
    print(f"  {'ID':<5}{'Title':<26}{'Priority':<10}{'Status':<13}{'Assigned To':<15}")
    print("  " + "-" * 68)
    for t in tickets:
        print(f"  {t.ticket_id:<5}{t.title[:24]:<26}{t.priority:<10}"
              f"{t.status:<13}{t.assigned_to:<15}")


def pause():
    input("\nPress Enter to continue...")


# --------------------------------------------------------------------
# MAIN MENU LOOP
# --------------------------------------------------------------------
def main():
    manager = TicketManager()

    MENU = """
==================================================
   HELP DESK / IT TICKET MANAGEMENT SYSTEM
==================================================
 1. Create ticket
 2. Assign ticket
 3. Update / close ticket status
 4. Search tickets
 5. Sort tickets (priority/date)
 6. View ticket history
 7. Generate summary report
 8. View all tickets
 9. Exit
==================================================
"""

    while True:
        print(MENU)
        choice = input("Enter your choice (1-9): ").strip()

        try:
            if choice == "1":
                title = input("Title: ")
                description = input("Description: ")
                priority = prompt_choice("Priority", PRIORITY_LEVELS)
                ticket = manager.create_ticket(title, description, priority)
                print(f"\n  Ticket #{ticket.ticket_id} created successfully.")

            elif choice == "2":
                ticket_id = int(input("Ticket ID to assign: "))
                assignee = input("Assign to (staff name): ")
                ticket = manager.assign_ticket(ticket_id, assignee)
                print(f"\n  Ticket #{ticket.ticket_id} now assigned to {ticket.assigned_to}.")

            elif choice == "3":
                ticket_id = int(input("Ticket ID to update: "))
                new_status = prompt_choice("New status", STATUS_LEVELS)
                ticket = manager.update_status(ticket_id, new_status)
                print(f"\n  Ticket #{ticket.ticket_id} status is now '{ticket.status}'.")

            elif choice == "4":
                keyword = input("Keyword (leave blank to skip): ").strip() or None
                status_in = input("Status filter (leave blank to skip): ").strip() or None
                priority_in = input("Priority filter (leave blank to skip): ").strip() or None
                results = manager.search_tickets(keyword, status_in, priority_in)
                print(f"\n  Found {len(results)} ticket(s):")
                print_ticket_table(results)

            elif choice == "5":
                by = prompt_choice("Sort by", ["priority", "date"])
                order = prompt_choice("Order", ["descending", "ascending"])
                results = manager.sort_tickets(by, descending=(order == "descending"))
                print(f"\n  Tickets sorted by {by} ({order}):")
                print_ticket_table(results)

            elif choice == "6":
                ticket_id = int(input("Ticket ID: "))
                history = manager.get_history(ticket_id)
                print(f"\n  History for ticket #{ticket_id}:")
                for entry in history:
                    print(f"    - {entry}")

            elif choice == "7":
                summary = manager.generate_summary()
                print("\n  ----- SUMMARY REPORT -----")
                print(f"  Total tickets: {summary['total_tickets']}")
                print("  By status:")
                for status, count in summary["by_status"].items():
                    print(f"    {status:<12}: {count}")
                print("  By priority:")
                for priority, count in summary["by_priority"].items():
                    print(f"    {priority:<12}: {count}")

            elif choice == "8":
                all_tickets = list(manager.tickets.values())
                print(f"\n  All tickets ({len(all_tickets)}):")
                print_ticket_table(all_tickets)

            elif choice == "9":
                print("\n  Data saved. Goodbye!")
                break

            else:
                print("\n  Invalid choice, please enter a number from 1-9.")

        except ValueError:
            print("\n  [Error] Please enter a valid whole number for the Ticket ID.")
        except TicketError as e:
            print(f"\n  [Error] {e}")

        pause()


if __name__ == "__main__":
    main()
