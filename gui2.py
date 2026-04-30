import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os
from pathlib import Path
import io

# tenants and boarding house limitssz
MAX_BOARDING_HOUSES = 10
MAX_ROOMMATES_PER_DORM = 5                       

class ShareStayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ShareStay - Dorm Expense Splitter")
        self.root.geometry("1368x768")
        self.root.configure(bg="#1e3a5f")
       
        self.boarding_house_no = None
        self.tenants = {}
        self.expenses = []
        self.data_file = "sharestay_data.json"
       
        self.load_data()
        self.show_login_window()
       
    def show_login_window(self):
        """Display the login/dorm number entry window"""
        self.clear_window()
       
        # frame for bg
        bg_frame = tk.Frame(self.root, bg="#1e3a5f")
        bg_frame.pack(fill=tk.BOTH, expand=True)
       
       
        # header w logo
        header_frame = tk.Frame(bg_frame, bg="#2c5aa0", height=120)
        header_frame.pack(fill=tk.X)
       
        logo_label = tk.Label(header_frame, text="🏠", font=("Arial", 40), bg="#2c5aa0", fg="white")
        logo_label.pack(pady=10)
       
        title_label = tk.Label(header_frame, text="SHARESTAY", font=("Arial", 32, "bold"), bg="#2c5aa0", fg="white")
        title_label.pack(pady=10)
       
        # Main contents
        content_frame = tk.Frame(bg_frame, bg="#4a7ba7")
        content_frame.pack(fill=tk.BOTH, expand=True)
       
        center_frame = tk.Frame(content_frame, bg="#4a7ba7")
        center_frame.pack(expand=True)
       
        prompt_label = tk.Label(center_frame, text="Select Boarding House or Add New One",font=("Arial", 14, "italic"), bg="#4a7ba7", fg="white")
        prompt_label.pack(pady=20)
       
        # Dorm selection frame
        selection_frame = tk.Frame(center_frame, bg="#4a7ba7")
        selection_frame.pack(pady=10)
       
        tk.Label(selection_frame, text="Enter Boarding House Number:", font=("Arial", 12), bg="#4a7ba7", fg="white").pack(pady=5)
       
        # Input field
        input_frame = tk.Frame(center_frame, bg="#4a7ba7")
        input_frame.pack(pady=10)
       
        self.dorm_entry = tk.Entry(input_frame, font=("Arial", 16), width=40, bg="#3d5a80", fg="white", insertbackground="white")
        self.dorm_entry.pack(pady=10, ipady=10)
        self.dorm_entry.bind("<Return>", lambda e: self.login_dorm())
       
        # Button frame
        button_frame = tk.Frame(center_frame, bg="#4a7ba7")
        button_frame.pack(pady=20)
       
        login_btn = tk.Button(button_frame, text="Enter", command=self.login_dorm,  font=("Arial", 14, "bold"), bg="#1e3a5f", fg="white", padx=30, pady=10, cursor="hand2")
        login_btn.pack(side=tk.LEFT, padx=10)
       
        search_btn = tk.Button(button_frame, text="Search All Boarding Houses", command=self.search_all_boarding_houses, font=("Arial", 14, "bold"), bg="#2c5aa0", fg="white",padx=20, pady=10, cursor="hand2")
        search_btn.pack(side=tk.LEFT, padx=10)
       
    def search_all_boarding_houses(self):
        """Search and display all boarding houses list"""
        window = tk.Toplevel(self.root)
        window.title("All Boarding Houses")
        window.geometry("600x500")
        window.configure(bg="#2c5aa0")
       
        tk.Label(window, text="All Boarding Houses", font=("Arial", 16, "bold"),
                bg="#2c5aa0", fg="white").pack(pady=10)
       
        # Display stats
        stats_text = f"Total: {len(self.tenants)}/{MAX_BOARDING_HOUSES} | Max Roommates per Dorm: {MAX_ROOMMATES_PER_DORM}"
        tk.Label(window, text=stats_text, font=("Arial", 10),
                bg="#2c5aa0", fg="#b0c4ff").pack(pady=5)
       
        # Create listbox for boarding houses
        list_frame = tk.Frame(window, bg="#2c5aa0")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
       
        tk.Label(list_frame, text="Click on a Boarding House to View Transactions:", 
                font=("Arial", 11), bg="#2c5aa0", fg="white").pack(pady=5)
       
        boarding_house_list = tk.Listbox(list_frame, font=("Arial", 12), 
                                        bg="#3d5a80", fg="white", 
                                        selectmode=tk.SINGLE, height=15)
        boarding_house_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        scrollbar = tk.Scrollbar(list_frame, command=boarding_house_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        boarding_house_list.config(yscrollcommand=scrollbar.set)
       
        # Populate listbox
        if not self.tenants:
            boarding_house_list.insert(tk.END, "No boarding houses found.")
        else:
            for dorm_no, tenants in sorted(self.tenants.items()):
                room_count = len(tenants)
                boarding_house_list.insert(tk.END, f"Boarding House {dorm_no} ({room_count}/{MAX_ROOMMATES_PER_DORM} rooms)")
       
        def enter_boarding_house():
            """Enter the selected boarding house"""
            selection = boarding_house_list.curselection()
            if not selection:
                messagebox.showwarning("Select", "Please select a boarding house!")
                return
           
            selected_text = boarding_house_list.get(selection[0])
            dorm_no = selected_text.split()[2]
           
            self.boarding_house_no = dorm_no
            window.destroy()
            self.show_main_dashboard()
       
        # Double-click to enter
        boarding_house_list.bind("<Double-Button-1>", lambda e: enter_boarding_house())
       
        def view_transactions():
            """Display transactions for selected boarding house"""
            selection = boarding_house_list.curselection()
            if not selection:
                messagebox.showwarning("Select", "Please select a boarding house!")
                return
               
            selected_text = boarding_house_list.get(selection[0])
            dorm_no = selected_text.split()[2]
               
            # Create new window for transactions
            trans_window = tk.Toplevel(window)
            trans_window.title(f"Transactions - Boarding House {dorm_no}")
            trans_window.geometry("700x600")
            trans_window.configure(bg="#2c5aa0")
               
            tk.Label(trans_window, text=f"Boarding House {dorm_no} - Transaction History", 
                    font=("Arial", 14, "bold"), bg="#2c5aa0", fg="white").pack(pady=10)
               
            # Create text display
            text_frame = tk.Frame(trans_window, bg="#2c5aa0")
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
               
            display_text = tk.Text(text_frame, bg="#1e3a5f", fg="white",
                                  font=("Arial", 10), state=tk.DISABLED, wrap=tk.WORD)
            display_text.pack(fill=tk.BOTH, expand=True)
               
            scrollbar2 = tk.Scrollbar(text_frame, command=display_text.yview)
            scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
            display_text.config(yscrollcommand=scrollbar2.set)
               
            # Populate with boarding house info
            display_text.config(state=tk.NORMAL)
            display_text.delete(1.0, tk.END)
               
            tenants = self.tenants.get(dorm_no, {})
            dorm_expenses = [e for e in self.expenses if e["dorm"] == dorm_no]
               
            # Roommates
            display_text.insert(tk.END, "ROOMMATES:\n")
            display_text.insert(tk.END, "-" * 60 + "\n")
            if tenants:
                for name in tenants:
                    display_text.insert(tk.END, f"• {name}\n")
            else:
                display_text.insert(tk.END, "No roommates added.\n")
               
            # Transactions
            display_text.insert(tk.END, "\n\nTRANSACTIONS:\n")
            display_text.insert(tk.END, "-" * 60 + "\n")
               
            if dorm_expenses:
                total = 0
                for i, exp in enumerate(dorm_expenses, 1):
                    display_text.insert(tk.END, f"{i}. {exp['description']}\n")
                    display_text.insert(tk.END, f"Amount: ₱{exp['amount']:.2f}\n")
                    display_text.insert(tk.END, f"Category: {exp['category']}\n")
                    display_text.insert(tk.END, f"Paid by: {exp['payer']}\n")
                    display_text.insert(tk.END, f"Date: {exp['date']}\n\n")
                    total += exp['amount']
                display_text.insert(tk.END, f"TOTAL TRANSACTIONS: ₱{total:.2f}\n")
            else:
                display_text.insert(tk.END, "No transactions recorded.\n")
               
            display_text.config(state=tk.DISABLED)
       
        # View button
        view_btn = tk.Button(window, text="View Transactions", command=view_transactions,
                            font=("Arial", 12, "bold"), bg="#1e3a5f", fg="white",
                            padx=20, pady=10, cursor="hand2")
        view_btn.pack(pady=10)
        
        # Enter button
        enter_btn = tk.Button(window, text="Enter Boarding House", command=enter_boarding_house,
                             font=("Arial", 12, "bold"), bg="#2c5aa0", fg="white",
                             padx=20, pady=10, cursor="hand2")
        enter_btn.pack(pady=5)
       
    def login_dorm(self):
        """Handle dorm number entry"""
        dorm_no = self.dorm_entry.get().strip()
        if not dorm_no:
            messagebox.showerror("Error", "Please enter a boarding house number!")
            return
       
        # Check if already exists or if we can add a new one
        if dorm_no not in self.tenants:
            if len(self.tenants) >= MAX_BOARDING_HOUSES:
                messagebox.showerror("Limit Reached", 
                    f"Maximum boarding houses ({MAX_BOARDING_HOUSES}) reached!\n"
                    f"Current: {len(self.tenants)}/{MAX_BOARDING_HOUSES}")
                return
            self.tenants[dorm_no] = {}
       
        self.boarding_house_no = dorm_no
        self.show_main_dashboard()
       
    def show_main_dashboard(self):
        """Display the main dashboard with all options"""
        self.clear_window()
       
        # Header
        header_frame = tk.Frame(self.root, bg="#2c5aa0", height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
       
        header_content = tk.Frame(header_frame, bg="#2c5aa0")
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
       
        # Logo and Title on the same line, centered
        logo_label = tk.Label(header_content, text="🏠", font=("Arial", 50),
                             bg="#2c5aa0", fg="white")
        logo_label.pack(side=tk.LEFT, padx=10)
       
        title_label = tk.Label(header_content, text="SHARESTAY", 
                              font=("Arial", 36, "bold"), bg="#2c5aa0", fg="white")
        title_label.pack(side=tk.LEFT, padx=20)
       
        # Spacing
        spacer = tk.Frame(header_content, bg="#2c5aa0")
        spacer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
       
        # Dorm info on the right
        dorm_label = tk.Label(header_content,
                             text=f"Boarding House No. {self.boarding_house_no}",
                             font=("Arial", 14, "bold"), bg="#2c5aa0", fg="#b0c4ff")
        dorm_label.pack(side=tk.RIGHT, padx=20)
       
        # Main content area
        content_frame = tk.Frame(self.root, bg="#4a7ba7")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
       
        # Display area (right side)
        display_frame = tk.Frame(content_frame, bg="#2c5aa0", relief=tk.RAISED, bd=2)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
       
        self.display_text = tk.Text(display_frame, bg="#1e3a5f", fg="white",
                                   font=("Arial", 11), state=tk.DISABLED, wrap=tk.WORD)
        self.display_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
       
        scrollbar = tk.Scrollbar(display_frame, command=self.display_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.display_text.config(yscrollcommand=scrollbar.set)
       
        # Buttons area (left side)
        buttons_frame = tk.Frame(content_frame, bg="#4a7ba7")
        buttons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
       
        # Create button grid
        button_specs = [
            ("Add Roommate", self.add_roommate_window),
            ("View Roommates", self.view_roommates),
            ("Add Expenses", self.add_expense_window),
            ("View Expenses", self.view_expenses),
            ("Calculate Expense Split", self.calculate_split),
            ("Who Haven't Paid", self.who_havent_paid),
            ("Record Payment", self.record_payment_window),
            ("Summary (All)", self.generate_summary),
            ("Clear History", self.clear_history_menu),
        ]
       
        for i, (text, command) in enumerate(button_specs):
            row = i // 2
            col = i % 2
            btn = tk.Button(buttons_frame, text=text, command=command,
                           font=("Arial", 11, "bold"), bg="#1e3a5f", fg="white",
                           padx=10, pady=15, cursor="hand2", relief=tk.RAISED, bd=2)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
       
        # Configure grid weights
        for i in range(5):
            buttons_frame.grid_rowconfigure(i, weight=1)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
       
        # Bottom buttons frame for Homepage and Exit
        bottom_buttons_frame = tk.Frame(buttons_frame, bg="#4a7ba7")
        bottom_buttons_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
       
        # Homepage button
        homepage_btn = tk.Button(bottom_buttons_frame, text="Homepage", command=self.go_to_homepage,
                                font=("Arial", 11, "bold"), bg="#2c5aa0", fg="white",
                                padx=15, pady=10, cursor="hand2")
        homepage_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
       
        # Exit button
        exit_btn = tk.Button(bottom_buttons_frame, text="Exit", command=self.exit_app,
                            font=("Arial", 11, "bold"), bg="#c41e3a", fg="white",
                            padx=15, pady=10, cursor="hand2")
        exit_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
       
        self.display_dashboard_info()

    def go_to_homepage(self):
        """Return to the login/home page"""
        self.save_data()
        self.boarding_house_no = None
        self.show_login_window()
       
    def display_dashboard_info(self):
        """Display initial dashboard information"""
        dorm_expenses = [e for e in self.expenses if e["dorm"] == self.boarding_house_no]
        total = sum(e["amount"] for e in dorm_expenses)
        current_roommates = len(self.tenants.get(self.boarding_house_no, {}))
        
        self.update_display("SHARESTAY DASHBOARD\n")
        self.update_display("=" * 50 + "\n\n")
        self.update_display(f"Boarding House: {self.boarding_house_no}\n")
        self.update_display(f"Total Roommates: {current_roommates}/{MAX_ROOMMATES_PER_DORM}\n")
        self.update_display(f"Total Expenses: {len(dorm_expenses)}\n")
        self.update_display(f"Total Amount: ₱{total:.2f}\n\n")
        self.update_display("Select an option from the left to get started.\n")
       
    def add_roommate_window(self):
        """Open window to add a new roommate"""
        current_count = len(self.tenants.get(self.boarding_house_no, {}))
        
        if current_count >= MAX_ROOMMATES_PER_DORM:
            messagebox.showerror("Limit Reached", 
                f"Maximum roommates ({MAX_ROOMMATES_PER_DORM}) reached for this boarding house!\n"
                f"Current: {current_count}/{MAX_ROOMMATES_PER_DORM}")
            return
        
        window = tk.Toplevel(self.root)
        window.title("Add Roommate")
        window.geometry("400x250")
        window.configure(bg="#2c5aa0")
       
        tk.Label(window, text="Add New Roommate", font=("Arial", 16, "bold"),
                bg="#2c5aa0", fg="white").pack(pady=10)
       
        # Display current count
        count_label = tk.Label(window, text=f"Roommates: {current_count}/{MAX_ROOMMATES_PER_DORM}", 
                              font=("Arial", 10), bg="#2c5aa0", fg="#b0c4ff")
        count_label.pack(pady=5)
       
        tk.Label(window, text="Roommate Name:", font=("Arial", 12),
                bg="#2c5aa0", fg="white").pack(pady=5)
        name_entry = tk.Entry(window, font=("Arial", 12), width=30)
        name_entry.pack(pady=5, ipady=5)
       
        tk.Label(window, text="Move-in Date (YYYY-MM-DD):", font=("Arial", 12),
                bg="#2c5aa0", fg="white").pack(pady=5)
        date_entry = tk.Entry(window, font=("Arial", 12), width=30)
        date_entry.pack(pady=5, ipady=5)
       
        def save_roommate():
            name = name_entry.get().strip()
            date = date_entry.get().strip()
           
            if not name or not date:
                messagebox.showerror("Error", "Please fill all fields!")
                return
           
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
           
            if name in self.tenants[self.boarding_house_no]:
                messagebox.showerror("Error", "Roommate already exists!")
                return
           
            self.tenants[self.boarding_house_no][name] = {
                "move_in_date": date,
                "balance": 0,
                "paid": 0,
                "owes": 0
            }
           
            self.save_data()
            messagebox.showinfo("Success", f"{name} added successfully!")
            self.update_display(f"✓ {name} added to the boarding house!\n")
            window.destroy()
       
        tk.Button(window, text="Save", command=save_roommate,
                 font=("Arial", 12, "bold"), bg="#1e3a5f", fg="white",
                 padx=20, pady=10).pack(pady=20)
       
    def view_roommates(self):
        """Display all roommates"""
        self.update_display("")
        self.update_display("ROOMMATES LIST\n")
        self.update_display("=" * 50 + "\n\n")
       
        roommates = self.tenants.get(self.boarding_house_no, {})
        if not roommates:
            self.update_display("No roommates added yet.\n")
            return
       
        for name, info in roommates.items():
            self.update_display(f"Name: {name}\n")
            self.update_display(f"Move-in Date: {info['move_in_date']}\n")
            self.update_display(f"Balance: ₱{info['balance']:.2f}\n")
            self.update_display(f"Paid: ₱{info['paid']:.2f}\n")
            self.update_display(f"Owes: ₱{info['owes']:.2f}\n\n")
       
    def add_expense_window(self):
        """Open window to add an expense"""
        window = tk.Toplevel(self.root)
        window.title("Add Expense")
        window.geometry("450x450")
        window.configure(bg="#2c5aa0")
       
        tk.Label(window, text="Add New Expense", font=("Arial", 16, "bold"),
                bg="#2c5aa0", fg="white").pack(pady=10)
       
        # Description
        tk.Label(window, text="Description:", font=("Arial", 11),
                bg="#2c5aa0", fg="white").pack(pady=3)
        desc_entry = tk.Entry(window, font=("Arial", 11), width=35)
        desc_entry.pack(pady=3, ipady=5)
       
        # Amount
        tk.Label(window, text="Amount (₱):", font=("Arial", 11),
                bg="#2c5aa0", fg="white").pack(pady=3)
        amount_entry = tk.Entry(window, font=("Arial", 11), width=35)
        amount_entry.pack(pady=3, ipady=5)
       
        # Category
        tk.Label(window, text="Category:", font=("Arial", 11),
                bg="#2c5aa0", fg="white").pack(pady=3)
        category_var = tk.StringVar(value="Groceries")
        categories = ["Electricity", "Water", "Groceries", "Internet", "Rent", "Other"]
        category_menu = ttk.Combobox(window, textvariable=category_var,
                                     values=categories, width=32, state="readonly")
        category_menu.pack(pady=3, ipady=3)
       
        # Payer
        tk.Label(window, text="Who Paid:", font=("Arial", 11),
                bg="#2c5aa0", fg="white").pack(pady=3)
        payer_var = tk.StringVar()
        roommates = list(self.tenants.get(self.boarding_house_no, {}).keys())
        payer_menu = ttk.Combobox(window, textvariable=payer_var,
                                 values=roommates, width=32, state="readonly")
        payer_menu.pack(pady=3, ipady=3)
       
        # Date
        tk.Label(window, text="Date (YYYY-MM-DD):", font=("Arial", 11),
                bg="#2c5aa0", fg="white").pack(pady=3)
        date_entry = tk.Entry(window, font=("Arial", 11), width=35)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(pady=3, ipady=5)
       
        def save_expense():
            desc = desc_entry.get().strip()
            amount_str = amount_entry.get().strip()
            category = category_var.get()
            payer = payer_var.get()
            date = date_entry.get().strip()
           
            if not all([desc, amount_str, category, payer, date]):
                messagebox.showerror("Error", "Please fill all fields!")
                return
           
            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid amount! Enter a positive number.")
                return
           
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
           
            expense = {
                "description": desc,
                "amount": amount,
                "category": category,
                "payer": payer,
                "date": date,
                "dorm": self.boarding_house_no,
                "involved": list(self.tenants[self.boarding_house_no].keys())
            }
           
            self.expenses.append(expense)
           
            # Update payer's balance
            self.tenants[self.boarding_house_no][payer]["paid"] += amount
           
            self.save_data()
            messagebox.showinfo("Success", "Expense added successfully!")
            self.update_display(f"✓ Expense added: {desc} - ₱{amount:.2f}\n")
            window.destroy()
       
        tk.Button(window, text="Save Expense", command=save_expense,
                 font=("Arial", 12, "bold"), bg="#1e3a5f", fg="white",
                 padx=20, pady=10).pack(pady=15)
       
    def view_expenses(self):
        """Display all expenses"""
        self.update_display("")
        self.update_display("EXPENSE HISTORY\n")
        self.update_display("=" * 50 + "\n\n")
       
        dorm_expenses = [e for e in self.expenses if e["dorm"] == self.boarding_house_no]
       
        if not dorm_expenses:
            self.update_display("No expenses recorded yet.\n")
            return
       
        for i, exp in enumerate(dorm_expenses, 1):
            self.update_display(f"{i}. {exp['description']}\n")
            self.update_display(f"Amount: ₱{exp['amount']:.2f}\n")
            self.update_display(f"Category: {exp['category']}\n")
            self.update_display(f"Paid by: {exp['payer']}\n")
            self.update_display(f"Date: {exp['date']}\n\n")
       
    def calculate_split(self):
        """Calculate and display expense splits - Everyone pays their share including the payer"""
        self.update_display("")
        self.update_display("EXPENSE SPLIT CALCULATION\n")
        self.update_display("=" * 50 + "\n\n")
       
        dorm_expenses = [e for e in self.expenses if e["dorm"] == self.boarding_house_no]
        roommates = list(self.tenants.get(self.boarding_house_no, {}).keys())
       
        if not dorm_expenses or not roommates:
            self.update_display("No expenses or roommates to split.\n")
            return
       
        # Calculate splits - Everyone including the payer owes their share
        splits = {name: {"owes": 0, "paid": 0} for name in roommates}
       
        for exp in dorm_expenses:
            # Split the expense among ALL involved people (including the payer)
            per_person = exp["amount"] / len(exp["involved"])
            splits[exp["payer"]]["paid"] += exp["amount"]
           
            # Everyone involved owes their share (including the payer)
            for person in exp["involved"]:
                splits[person]["owes"] += per_person
       
        self.update_display("Split Breakdown:\n\n")
        for name, amounts in splits.items():
            # Payer's balance = what they paid - what they owe (their fair share)
            balance = amounts["paid"] - amounts["owes"]
            self.update_display(f"{name}:\n")
            self.update_display(f"Paid Total: ₱{amounts['paid']:.2f}\n")
            self.update_display(f"Fair Share (Owes): ₱{amounts['owes']:.2f}\n")
            
            if balance > 0:
                self.update_display(f"Should Receive: ₱{balance:.2f}\n\n")
            elif balance < 0:
                self.update_display(f"Should Pay: ₱{abs(balance):.2f}\n\n")
            else:
                self.update_display(f"Settled! ✓\n\n")
       
    def who_havent_paid(self):
        """Show who hasn't settled their expenses with payment tracking"""
        self.update_display("")
        self.update_display("WHO HAVEN'T PAID\n")
        self.update_display("=" * 50 + "\n\n")
       
        dorm_expenses = [e for e in self.expenses if e["dorm"] == self.boarding_house_no]
        roommates = list(self.tenants.get(self.boarding_house_no, {}).keys())
       
        if not dorm_expenses or not roommates:
            self.update_display("No expenses recorded yet.\n")
            return
       
        # Calculate who owes whom
        balances = {name: {"paid": 0, "owes": 0} for name in roommates}
       
        for exp in dorm_expenses:
            if "is_payment" not in exp or not exp.get("is_payment"):
                # Regular expense - everyone including payer owes their fair share
                per_person = exp["amount"] / len(exp["involved"])
                balances[exp["payer"]]["paid"] += exp["amount"]
                for person in exp["involved"]:
                    balances[person]["owes"] += per_person
            else:
                # Payment transaction
                payer = exp["payer"]
                involved = exp.get("involved", [])
                if len(involved) > 1:
                    receiver = [p for p in involved if p != payer][0]
                    # Reduce the payer's owed amount (they are paying off their debt)
                    balances[payer]["owes"] = max(0, balances[payer]["owes"] - exp["amount"])
       
        self.update_display("Outstanding Balances:\n\n")
        has_debt = False
        
        for name, balance_info in balances.items():
            net_balance = balance_info["paid"] - balance_info["owes"]
            
            # Show BOTH who needs to pay AND who is owed money
            if net_balance < 0:
                has_debt = True
                self.update_display(f"❌ {name} NEEDS TO PAY: ₱{abs(net_balance):.2f}\n")
            elif net_balance > 0:
                self.update_display(f"💰 {name} SHOULD RECEIVE: ₱{net_balance:.2f}\n")
            else:
                # Balance is exactly 0 (perfect settlement)
                self.update_display(f"✅ {name} - SPLIT SETTLED\n")
       
        if not has_debt:
            # Check if anyone has exactly 0 balance
            anyone_settled = any((balance_info["paid"] - balance_info["owes"]) == 0 
                                for balance_info in balances.values())
            if anyone_settled:
                self.update_display("\n✅ All balances are settled! 🎉\n")
            else:
                self.update_display("\n✅ Everyone is settled up! 🎉\n")
                self.update_display("\nAll debts have been cleared.\n")
       
    def record_payment_window(self):
        """Record a payment between roommates"""
        window = tk.Toplevel(self.root)
        window.title("Record Payment")
        window.geometry("400x300")
        window.configure(bg="#2c5aa0")
       
        tk.Label(window, text="Record Payment", font=("Arial", 16, "bold"),
                bg="#2c5aa0", fg="white").pack(pady=10)
       
        roommates = list(self.tenants.get(self.boarding_house_no, {}).keys())
       
        tk.Label(window, text="From (Who Pays):", font=("Arial", 11),
                bg="#2c5aa0", fg="white").pack(pady=5)
        from_var = tk.StringVar()
        from_menu = ttk.Combobox(window, textvariable=from_var,
                                values=roommates, width=32, state="readonly")
        from_menu.pack(pady=5, ipady=3)
       
        tk.Label(window, text="To (Who Receives):", font=("Arial", 11),
                bg="#2c5aa0", fg="white").pack(pady=5)
        to_var = tk.StringVar()
        to_menu = ttk.Combobox(window, textvariable=to_var,
                              values=roommates, width=32, state="readonly")
        to_menu.pack(pady=5, ipady=3)
       
        tk.Label(window, text="Amount (₱):", font=("Arial", 11),
                bg="#2c5aa0", fg="white").pack(pady=5)
        amount_entry = tk.Entry(window, font=("Arial", 11), width=35)
        amount_entry.pack(pady=5, ipady=5)
       
        def save_payment():
            from_person = from_var.get()
            to_person = to_var.get()
            amount_str = amount_entry.get().strip()
           
            if not all([from_person, to_person, amount_str]):
                messagebox.showerror("Error", "Please fill all fields!")
                return
           
            if from_person == to_person:
                messagebox.showerror("Error", "Cannot pay to yourself!")
                return
           
            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid amount!")
                return
           
            # Record payment as an expense
            expense = {
                "description": f"Payment: {from_person} → {to_person}",
                "amount": amount,
                "category": "Payment",
                "payer": from_person,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "dorm": self.boarding_house_no,
                "involved": [from_person, to_person],
                "is_payment": True
            }
           
            self.expenses.append(expense)
            self.save_data()
            messagebox.showinfo("Success", f"Payment recorded: {from_person} paid ₱{amount:.2f} to {to_person}")
            self.update_display(f"✓ Payment recorded: {from_person} → {to_person} = ₱{amount:.2f}\n")
            window.destroy()
       
        tk.Button(window, text="Record Payment", command=save_payment,
                 font=("Arial", 12, "bold"), bg="#1e3a5f", fg="white",
                 padx=20, pady=10).pack(pady=15)
       
    def generate_summary(self):
        """Generate comprehensive summary report with settlement status"""
        self.update_display("")
        self.update_display("COMPREHENSIVE SUMMARY\n")
        self.update_display("=" * 50 + "\n\n")
       
        dorm_expenses = [e for e in self.expenses if e["dorm"] == self.boarding_house_no]
       
        if not dorm_expenses:
            self.update_display("No expenses to summarize.\n")
            return
       
        # Total expenses
        total = sum(e["amount"] for e in dorm_expenses)
       
        # By category
        self.update_display("Expenses by Category:\n")
        categories = {}
        for exp in dorm_expenses:
            cat = exp.get("category", "Other")
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += exp["amount"]
       
        for cat, amount in sorted(categories.items()):
            self.update_display(f"{cat}: ₱{amount:.2f}\n")
       
        self.update_display("\n")
       
        # By payer
        self.update_display("Expenses by Payer:\n")
        payers = {}
        for exp in dorm_expenses:
            payer = exp["payer"]
            if payer not in payers:
                payers[payer] = 0
            payers[payer] += exp["amount"]
       
        for payer, amount in sorted(payers.items()):
            self.update_display(f"{payer}: ₱{amount:.2f}\n")
        
        self.update_display("\n")
        self.update_display("=" * 50 + "\n")
        self.update_display("SETTLEMENT STATUS\n")
        self.update_display("=" * 50 + "\n\n")
        
        # Calculate settlement status
        roommates = list(self.tenants.get(self.boarding_house_no, {}).keys())
        balances = {name: {"paid": 0, "owes": 0} for name in roommates}
        
        for exp in dorm_expenses:
            if "is_payment" not in exp or not exp.get("is_payment"):
                # Regular expense - everyone including payer owes their fair share
                per_person = exp["amount"] / len(exp["involved"])
                balances[exp["payer"]]["paid"] += exp["amount"]
                for person in exp["involved"]:
                    balances[person]["owes"] += per_person
            else:
                # Payment transaction
                payer = exp["payer"]
                involved = exp.get("involved", [])
                if len(involved) > 1:
                    receiver = [p for p in involved if p != payer][0]
                    # Reduce the payer's owed amount
                    balances[payer]["owes"] = max(0, balances[payer]["owes"] - exp["amount"])
        
        # Display settlement details
        all_settled = True
        for name, balance_info in balances.items():
            net_balance = balance_info["paid"] - balance_info["owes"]
            
            if net_balance < 0:
                all_settled = False
                self.update_display(f"❌ {name}:\n")
                self.update_display(f"   Paid: ₱{balance_info['paid']:.2f}\n")
                self.update_display(f"   Fair Share: ₱{balance_info['owes']:.2f}\n")
                self.update_display(f"   NEEDS TO PAY: ₱{abs(net_balance):.2f}\n\n")
            elif net_balance > 0:
                self.update_display(f"💰 {name}:\n")
                self.update_display(f"   Paid: ₱{balance_info['paid']:.2f}\n")
                self.update_display(f"   Fair Share: ₱{balance_info['owes']:.2f}\n")
                self.update_display(f"   SHOULD RECEIVE: ₱{net_balance:.2f}\n\n")
            else:
                self.update_display(f"✅ {name}:\n")
                self.update_display(f"   Paid: ₱{balance_info['paid']:.2f}\n")
                self.update_display(f"   Fair Share: ₱{balance_info['owes']:.2f}\n")
                self.update_display(f"   STATUS: SPLIT SETTLED ✓\n\n")
        
        self.update_display("=" * 50 + "\n")
        if all_settled:
            self.update_display("✅ ALL DEBTS CLEARED! 🎉\n")
            self.update_display("Everyone is settled up!\n")
        else:
            self.update_display("⚠️  PENDING SETTLEMENTS\n")
            self.update_display("Some tenants need to complete payments.\n")
        self.update_display("=" * 50 + "\n")

    def clear_history_menu(self):
        """Open menu for different clear history options"""
        window = tk.Toplevel(self.root)
        window.title("Clear History - Select Option")
        window.geometry("450x300")
        window.configure(bg="#2c5aa0")
        
        tk.Label(window, text="What would you like to clear?", font=("Arial", 16, "bold"),
                bg="#2c5aa0", fg="white").pack(pady=20)
        
        def clear_roommates_only():
            if messagebox.askyesno("Confirm", "Clear all roommates from this boarding house?\nExpenses will remain."):
                self.tenants[self.boarding_house_no] = {}
                self.save_data()
                messagebox.showinfo("Success", "All roommates cleared!")
                self.update_display("")
                window.destroy()
        
        def clear_expenses_only():
            if messagebox.askyesno("Confirm", "Clear all expenses from this boarding house?\nRoommates will remain."):
                self.expenses = [e for e in self.expenses if e["dorm"] != self.boarding_house_no]
                for tenant in self.tenants[self.boarding_house_no].values():
                    tenant["paid"] = 0
                    tenant["owes"] = 0
                    tenant["balance"] = 0
                self.save_data()
                messagebox.showinfo("Success", "All expenses cleared!")
                self.update_display("")
                window.destroy()
        
        def clear_all_data():
            if messagebox.askyesno("Confirm", "Clear EVERYTHING for this boarding house?\nThis will delete all roommates and expenses!"):
                self.tenants[self.boarding_house_no] = {}
                self.expenses = [e for e in self.expenses if e["dorm"] != self.boarding_house_no]
                self.save_data()
                messagebox.showinfo("Success", "All data for this boarding house cleared!")
                self.update_display("")
                window.destroy()
        
        def clear_entire_file():
            if messagebox.askyesno("Confirm", "Delete the ENTIRE file?\nThis will remove ALL boarding houses and ALL data!\nThis cannot be undone!"):
                try:
                    os.remove(self.data_file)
                    self.tenants = {}
                    self.expenses = []
                    messagebox.showinfo("Success", "Entire database deleted!")
                    self.update_display("")
                    window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete file: {e}")
        
        # Button 1: Clear Roommates
        btn1 = tk.Button(window, text="1. Clear Roommate Names Only", command=clear_roommates_only,
                        font=("Arial", 11, "bold"), bg="#1e3a5f", fg="white",
                        padx=20, pady=12, cursor="hand2", width=35)
        btn1.pack(pady=8)
        
        # Button 2: Clear Expenses
        btn2 = tk.Button(window, text="2. Clear Expense History Only", command=clear_expenses_only,
                        font=("Arial", 11, "bold"), bg="#1e3a5f", fg="white",
                        padx=20, pady=12, cursor="hand2", width=35)
        btn2.pack(pady=8)
        
        # Button 3: Clear All for this dorm
        btn3 = tk.Button(window, text="3. Clear All Data (This Boarding House)", command=clear_all_data,
                        font=("Arial", 11, "bold"), bg="#c41e3a", fg="white",
                        padx=20, pady=12, cursor="hand2", width=35)
        btn3.pack(pady=8)
        
        # Button 4: Clear entire file
        btn4 = tk.Button(window, text="4. Clear Entire File (All Boarding Houses)", command=clear_entire_file,
                        font=("Arial", 11, "bold"), bg="#8b0000", fg="white",
                        padx=20, pady=12, cursor="hand2", width=35)
        btn4.pack(pady=8)
       
    def update_display(self, text):
        """Update the display text area"""
        self.display_text.config(state=tk.NORMAL)
        if text == "":
            self.display_text.delete(1.0, tk.END)
        else:
            self.display_text.insert(tk.END, text)
        self.display_text.see(tk.END)
        self.display_text.config(state=tk.DISABLED)
       
    def save_data(self):
        """Save data to file"""
        data = {
            "tenants": self.tenants,
            "expenses": self.expenses
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)
           
    def load_data(self):
        """Load data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.tenants = data.get("tenants", {})
                    self.expenses = data.get("expenses", [])
            except Exception as e:
                print(f"Error loading data: {e}")
               
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
           
    def exit_app(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.save_data()
            self.root.quit()




if __name__ == "__main__":
    root = tk.Tk()
    app = ShareStayApp(root)
    root.mainloop()