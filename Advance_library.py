import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
import json
import csv
import hashlib
import os
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class AdvancedLibraryManagementSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # Animation variables
        self.animation_running = False
        self.current_user = None
        self.user_role = None
        
        # Initialize database
        self.init_database()
        
        # Create GUI
        self.create_login_interface()
        
    def init_database(self):
        """Initialize SQLite database with all necessary tables"""
        self.conn = sqlite3.connect('library_system.db')
        self.cursor = self.conn.cursor()
        
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'member',
                full_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                registration_date TEXT,
                membership_status TEXT DEFAULT 'active',
                fine_balance REAL DEFAULT 0.0
            )
        ''')
        
        # Books table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT UNIQUE,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT,
                publisher TEXT,
                publication_year INTEGER,
                total_copies INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1,
                location TEXT,
                description TEXT,
                added_date TEXT,
                price REAL
            )
        ''')
        
        # Transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                transaction_type TEXT,
                issue_date TEXT,
                due_date TEXT,
                return_date TEXT,
                fine_amount REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        # Reservations table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                reservation_date TEXT,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        # Reviews table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                rating INTEGER,
                review_text TEXT,
                review_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        # Create default admin user
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password, role, full_name, email, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("admin", admin_password, "admin", "System Administrator", "admin@library.com", 
                  datetime.datetime.now().strftime("%Y-%m-%d")))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # Admin already exists
    
    def create_login_interface(self):
        """Create animated login interface"""
        self.login_frame = tk.Frame(self.root, bg='#2c3e50')
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Animated title
        self.title_label = tk.Label(self.login_frame, 
                                   text="📚 LIBRARY MANAGEMENT SYSTEM 📚",
                                   font=('Arial', 24, 'bold'),
                                   bg='#2c3e50', fg='#ecf0f1')
        self.title_label.pack(pady=50)
        
        # Login container with animation
        login_container = tk.Frame(self.login_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        login_container.pack(pady=50)
        login_container.configure(width=400, height=300)
        
        tk.Label(login_container, text="Login to System", font=('Arial', 18, 'bold'),
                bg='#34495e', fg='#ecf0f1').pack(pady=20)
        
        # Username
        tk.Label(login_container, text="Username:", font=('Arial', 12),
                bg='#34495e', fg='#ecf0f1').pack()
        self.username_entry = tk.Entry(login_container, font=('Arial', 12), width=25)
        self.username_entry.pack(pady=5)
        
        # Password
        tk.Label(login_container, text="Password:", font=('Arial', 12),
                bg='#34495e', fg='#ecf0f1').pack()
        self.password_entry = tk.Entry(login_container, font=('Arial', 12), width=25, show='*')
        self.password_entry.pack(pady=5)
        
        # Buttons
        login_btn = tk.Button(login_container, text="Login", font=('Arial', 12, 'bold'),
                             bg='#3498db', fg='white', command=self.login,
                             relief=tk.FLAT, padx=20)
        login_btn.pack(pady=10)
        
        register_btn = tk.Button(login_container, text="Register New Member", font=('Arial', 10),
                                bg='#e74c3c', fg='white', command=self.show_registration,
                                relief=tk.FLAT, padx=15)
        register_btn.pack(pady=5)
        
        # Start title animation
        self.animate_title()
    
    def animate_title(self):
        """Animate the title with color changes"""
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
        def change_color():
            if hasattr(self, 'title_label'):
                color = colors[int(time.time()) % len(colors)]
                self.title_label.configure(fg=color)
                self.root.after(1000, change_color)
        change_color()
    
    def login(self):
        """Authenticate user and show main interface"""
        username = self.username_entry.get()
        password = hashlib.sha256(self.password_entry.get().encode()).hexdigest()
        
        self.cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                           (username, password))
        user = self.cursor.fetchone()
        
        if user:
            self.current_user = user
            self.user_role = user[3]  # role column
            self.login_frame.destroy()
            self.create_main_interface()
        else:
            messagebox.showerror("Error", "Invalid username or password!")
    
    def show_registration(self):
        """Show member registration form"""
        reg_window = tk.Toplevel(self.root)
        reg_window.title("New Member Registration")
        reg_window.geometry("500x600")
        reg_window.configure(bg='#34495e')
        
        tk.Label(reg_window, text="New Member Registration", font=('Arial', 16, 'bold'),
                bg='#34495e', fg='#ecf0f1').pack(pady=20)
        
        # Registration form fields
        fields = ['Username', 'Password', 'Full Name', 'Email', 'Phone', 'Address']
        entries = {}
        
        for field in fields:
            tk.Label(reg_window, text=f"{field}:", font=('Arial', 12),
                    bg='#34495e', fg='#ecf0f1').pack(anchor='w', padx=50, pady=(10,0))
            entry = tk.Entry(reg_window, font=('Arial', 12), width=35)
            if field == 'Password':
                entry.configure(show='*')
            entry.pack(padx=50, pady=(0,5))
            entries[field] = entry
        
        def register_user():
            try:
                password_hash = hashlib.sha256(entries['Password'].get().encode()).hexdigest()
                self.cursor.execute('''
                    INSERT INTO users (username, password, full_name, email, phone, address, registration_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (entries['Username'].get(), password_hash, entries['Full Name'].get(),
                      entries['Email'].get(), entries['Phone'].get(), entries['Address'].get(),
                      datetime.datetime.now().strftime("%Y-%m-%d")))
                self.conn.commit()
                messagebox.showinfo("Success", "Registration successful!")
                reg_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Registration failed: {str(e)}")
        
        tk.Button(reg_window, text="Register", font=('Arial', 12, 'bold'),
                 bg='#2ecc71', fg='white', command=register_user,
                 relief=tk.FLAT, padx=30, pady=10).pack(pady=20)
    
    def create_main_interface(self):
        """Create the main application interface with all features"""
        # Main container
        self.main_frame = tk.Frame(self.root, bg='#2c3e50')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top menu bar
        self.create_menu_bar()
        
        # Status bar
        self.status_bar = tk.Label(self.root, text=f"Welcome, {self.current_user[4]} | Role: {self.user_role}", 
                                  bg='#34495e', fg='#ecf0f1', anchor='w')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Main content area with notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create all tabs
        self.create_dashboard_tab()
        self.create_books_tab()
        self.create_members_tab()
        self.create_transactions_tab()
        self.create_reports_tab()
        self.create_settings_tab()
        
        # Update status regularly
        self.update_status()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Books", command=self.import_books)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Send Notifications", command=self.send_notifications)
        tools_menu.add_command(label="Calculate Fines", command=self.calculate_fines)
        tools_menu.add_command(label="Generate Barcodes", command=self.generate_barcodes)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_dashboard_tab(self):
        """Create dashboard with statistics and charts"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Statistics cards
        stats_frame = tk.Frame(dashboard_frame, bg='#ecf0f1')
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Get statistics
        self.cursor.execute('SELECT COUNT(*) FROM books')
        total_books = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE role = "member"')
        total_members = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM transactions WHERE status = "active"')
        active_loans = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT SUM(fine_balance) FROM users')
        total_fines = self.cursor.fetchone()[0] or 0
        
        # Create stat cards
        stats = [
            ("Total Books", total_books, "#3498db"),
            ("Total Members", total_members, "#2ecc71"),
            ("Active Loans", active_loans, "#e74c3c"),
            ("Total Fines", f"${total_fines:.2f}", "#f39c12")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=color, relief=tk.RAISED, bd=2)
            card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
            
            tk.Label(card, text=str(value), font=('Arial', 24, 'bold'),
                    bg=color, fg='white').pack(pady=(20, 5))
            tk.Label(card, text=label, font=('Arial', 12),
                    bg=color, fg='white').pack(pady=(0, 20))
        
        # Charts area
        charts_frame = tk.Frame(dashboard_frame, bg='#ecf0f1')
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_charts(charts_frame)
    
    def create_charts(self, parent):
        """Create data visualization charts"""
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.patch.set_facecolor('#ecf0f1')
        
        # Chart 1: Books by category
        self.cursor.execute('SELECT category, COUNT(*) FROM books GROUP BY category')
        categories = self.cursor.fetchall()
        if categories:
            labels, sizes = zip(*categories)
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Books by Category')
        
        # Chart 2: Monthly registrations
        self.cursor.execute('''
            SELECT strftime('%Y-%m', registration_date) as month, COUNT(*) 
            FROM users WHERE role = 'member' 
            GROUP BY month ORDER BY month DESC LIMIT 6
        ''')
        registrations = self.cursor.fetchall()
        if registrations:
            months, counts = zip(*registrations)
            ax2.bar(months, counts)
            ax2.set_title('Member Registrations (Last 6 Months)')
            ax2.tick_params(axis='x', rotation=45)
        
        # Chart 3: Loan trends
        self.cursor.execute('''
            SELECT strftime('%Y-%m', issue_date) as month, COUNT(*) 
            FROM transactions 
            GROUP BY month ORDER BY month DESC LIMIT 12
        ''')
        loans = self.cursor.fetchall()
        if loans:
            months, counts = zip(*loans)
            ax3.plot(months, counts, marker='o')
            ax3.set_title('Loan Trends (Last 12 Months)')
            ax3.tick_params(axis='x', rotation=45)
        
        # Chart 4: Top borrowed books
        self.cursor.execute('''
            SELECT b.title, COUNT(t.id) as loan_count
            FROM books b
            JOIN transactions t ON b.id = t.book_id
            GROUP BY b.id
            ORDER BY loan_count DESC
            LIMIT 5
        ''')
        top_books = self.cursor.fetchall()
        if top_books:
            titles, counts = zip(*top_books)
            ax4.barh([title[:20] + '...' if len(title) > 20 else title for title in titles], counts)
            ax4.set_title('Top Borrowed Books')
        
        plt.tight_layout()
        
        # Embed chart in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_books_tab(self):
        """Create books management tab"""
        books_frame = ttk.Frame(self.notebook)
        self.notebook.add(books_frame, text="📚 Books")
        
        # Search and filter frame
        search_frame = tk.Frame(books_frame, bg='#ecf0f1')
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="Search:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.book_search_entry = tk.Entry(search_frame, width=30)
        self.book_search_entry.pack(side=tk.LEFT, padx=5)
        self.book_search_entry.bind('<KeyRelease>', self.search_books)
        
        tk.Button(search_frame, text="Add Book", command=self.add_book,
                 bg='#2ecc71', fg='white').pack(side=tk.RIGHT, padx=5)
        
        # Books treeview
        columns = ('ID', 'ISBN', 'Title', 'Author', 'Category', 'Available', 'Total')
        self.books_tree = ttk.Treeview(books_frame, columns=columns, show='headings')
        
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100)
        
        self.books_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Context menu for books
        self.books_context_menu = tk.Menu(self.root, tearoff=0)
        self.books_context_menu.add_command(label="Edit Book", command=self.edit_book)
        self.books_context_menu.add_command(label="Delete Book", command=self.delete_book)
        self.books_context_menu.add_command(label="View Details", command=self.view_book_details)
        self.books_context_menu.add_command(label="Add Review", command=self.add_book_review)
        
        self.books_tree.bind("<Button-3>", self.show_books_context_menu)
        
        self.load_books()
    
    def create_members_tab(self):
        """Create members management tab"""
        members_frame = ttk.Frame(self.notebook)
        self.notebook.add(members_frame, text="👥 Members")
        
        # Search frame
        search_frame = tk.Frame(members_frame, bg='#ecf0f1')
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="Search:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.member_search_entry = tk.Entry(search_frame, width=30)
        self.member_search_entry.pack(side=tk.LEFT, padx=5)
        self.member_search_entry.bind('<KeyRelease>', self.search_members)
        
        # Members treeview
        columns = ('ID', 'Username', 'Full Name', 'Email', 'Phone', 'Status', 'Fine Balance')
        self.members_tree = ttk.Treeview(members_frame, columns=columns, show='headings')
        
        for col in columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=120)
        
        self.members_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Context menu for members
        self.members_context_menu = tk.Menu(self.root, tearoff=0)
        self.members_context_menu.add_command(label="Edit Member", command=self.edit_member)
        self.members_context_menu.add_command(label="View History", command=self.view_member_history)
        self.members_context_menu.add_command(label="Suspend Member", command=self.suspend_member)
        self.members_context_menu.add_command(label="Send Message", command=self.send_message_to_member)
        
        self.members_tree.bind("<Button-3>", self.show_members_context_menu)
        
        self.load_members()
    
    def create_transactions_tab(self):
        """Create transactions management tab"""
        transactions_frame = ttk.Frame(self.notebook)
        self.notebook.add(transactions_frame, text="🔄 Transactions")
        
        # Transaction buttons
        btn_frame = tk.Frame(transactions_frame, bg='#ecf0f1')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        buttons = [
            ("Issue Book", self.issue_book, "#3498db"),
            ("Return Book", self.return_book, "#2ecc71"),
            ("Renew Book", self.renew_book, "#f39c12"),
            ("Reserve Book", self.reserve_book, "#9b59b6")
        ]
        
        for text, command, color in buttons:
            tk.Button(btn_frame, text=text, command=command,
                     bg=color, fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        
        # Transactions treeview
        columns = ('ID', 'Member', 'Book', 'Type', 'Issue Date', 'Due Date', 'Status', 'Fine')
        self.transactions_tree = ttk.Treeview(transactions_frame, columns=columns, show='headings')
        
        for col in columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=100)
        
        self.transactions_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.load_transactions()
    
    def create_reports_tab(self):
        """Create reports tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="📊 Reports")
        
        # Report buttons
        report_buttons = [
            ("Overdue Books Report", self.generate_overdue_report),
            ("Popular Books Report", self.generate_popular_books_report),
            ("Member Activity Report", self.generate_member_activity_report),
            ("Financial Report", self.generate_financial_report),
            ("Inventory Report", self.generate_inventory_report),
            ("Custom Report", self.create_custom_report)
        ]
        
        for i, (text, command) in enumerate(report_buttons):
            row = i // 2
            col = i % 2
            tk.Button(reports_frame, text=text, command=command,
                     bg='#34495e', fg='white', padx=30, pady=20,
                     width=25).grid(row=row, column=col, padx=20, pady=20)
        
        # Report display area
        self.report_text = tk.Text(reports_frame, height=15, width=80)
        self.report_text.grid(row=3, column=0, columnspan=2, padx=20, pady=20)
        
        scrollbar = tk.Scrollbar(reports_frame, orient="vertical", command=self.report_text.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.report_text.configure(yscrollcommand=scrollbar.set)
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # System settings
        system_frame = tk.LabelFrame(settings_frame, text="System Settings", 
                                    font=('Arial', 12, 'bold'))
        system_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Loan period setting
        tk.Label(system_frame, text="Default Loan Period (days):").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.loan_period_var = tk.StringVar(value="14")
        tk.Entry(system_frame, textvariable=self.loan_period_var, width=10).grid(row=0, column=1, padx=10, pady=5)
        
        # Fine per day
        tk.Label(system_frame, text="Fine per day ($):").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.fine_per_day_var = tk.StringVar(value="0.50")
        tk.Entry(system_frame, textvariable=self.fine_per_day_var, width=10).grid(row=1, column=1, padx=10, pady=5)
        
        # Max books per member
        tk.Label(system_frame, text="Max books per member:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.max_books_var = tk.StringVar(value="5")
        tk.Entry(system_frame, textvariable=self.max_books_var, width=10).grid(row=2, column=1, padx=10, pady=5)
        
        tk.Button(system_frame, text="Save Settings", command=self.save_settings,
                 bg='#2ecc71', fg='white').grid(row=3, column=0, columnspan=2, pady=10)
        
        # Database management
        db_frame = tk.LabelFrame(settings_frame, text="Database Management", 
                                font=('Arial', 12, 'bold'))
        db_frame.pack(fill=tk.X, padx=20, pady=10)
        
        db_buttons = [
            ("Backup Database", self.backup_database),
            ("Restore Database", self.restore_database),
            ("Optimize Database", self.optimize_database),
            ("Clear Old Records", self.clear_old_records)
        ]
        
        for i, (text, command) in enumerate(db_buttons):
            tk.Button(db_frame, text=text, command=command,
                     bg='#34495e', fg='white', padx=20, pady=5).grid(row=i//2, column=i%2, padx=10, pady=5)
    
    # Feature implementations
    def search_books(self, event=None):
        """Search books based on query"""
        query = self.book_search_entry.get()
        if query:
            self.cursor.execute('''
                SELECT id, isbn, title, author, category, available_copies, total_copies
                FROM books 
                WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        else:
            self.cursor.execute('SELECT id, isbn, title, author, category, available_copies, total_copies FROM books')
        
        books = self.cursor.fetchall()
        self.update_books_tree(books)
    
    def update_books_tree(self, books):
        """Update books treeview with data"""
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        for book in books:
            self.books_tree.insert('', 'end', values=book)
    
    def load_books(self):
        """Load all books into treeview"""
        self.cursor.execute('SELECT id, isbn, title, author, category, available_copies, total_copies FROM books')
        books = self.cursor.fetchall()
        self.update_books_tree(books)
    
    def add_book(self):
        """Add new book dialog"""
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Book")
        add_window.geometry("500x700")
        add_window.configure(bg='#ecf0f1')
        
        fields = ['ISBN', 'Title', 'Author', 'Category', 'Publisher', 'Publication Year', 
                 'Total Copies', 'Location', 'Price', 'Description']
        entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(add_window, text=f"{field}:", font=('Arial', 12),
                    bg='#ecf0f1').grid(row=i, column=0, padx=20, pady=10, sticky='w')
            
            if field == 'Description':
                entry = tk.Text(add_window, height=4, width=30)
            else:
                entry = tk.Entry(add_window, font=('Arial', 12), width=30)
            
            entry.grid(row=i, column=1, padx=20, pady=10)
            entries[field] = entry
        
        def save_book():
            try:
                # Get values
                values = {}
                for field, entry in entries.items():
                    if field == 'Description':
                        values[field] = entry.get('1.0', tk.END).strip()
                    else:
                        values[field] = entry.get()
                
                # Insert book
                self.cursor.execute('''
                    INSERT INTO books (isbn, title, author, category, publisher, publication_year,
                                     total_copies, available_copies, location, price, description, added_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (values['ISBN'], values['Title'], values['Author'], values['Category'],
                      values['Publisher'], int(values['Publication Year']), 
                      int(values['Total Copies']), int(values['Total Copies']),
                      values['Location'], float(values['Price']), values['Description'],
                      datetime.datetime.now().strftime("%Y-%m-%d")))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Book added successfully!")
                add_window.destroy()
                self.load_books()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add book: {str(e)}")
        
        tk.Button(add_window, text="Save Book", command=save_book,
                 bg='#2ecc71', fg='white', font=('Arial', 12, 'bold'),
                 padx=30, pady=10).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def edit_book(self):
        """Edit selected book"""
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to edit!")
            return
        
        book_id = self.books_tree.item(selected[0])['values'][0]
        
        # Get book details
        self.cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        book = self.cursor.fetchone()
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Book")
        edit_window.geometry("500x700")
        edit_window.configure(bg='#ecf0f1')
        
        fields = ['ISBN', 'Title', 'Author', 'Category', 'Publisher', 'Publication Year', 
                 'Total Copies', 'Location', 'Price', 'Description']
        entries = {}
        
        # Pre-fill with existing data
        book_data = {
            'ISBN': book[1], 'Title': book[2], 'Author': book[3], 'Category': book[4],
            'Publisher': book[5], 'Publication Year': book[6], 'Total Copies': book[7],
            'Location': book[9], 'Price': book[12], 'Description': book[10]
        }
        
        for i, field in enumerate(fields):
            tk.Label(edit_window, text=f"{field}:", font=('Arial', 12),
                    bg='#ecf0f1').grid(row=i, column=0, padx=20, pady=10, sticky='w')
            
            if field == 'Description':
                entry = tk.Text(edit_window, height=4, width=30)
                entry.insert('1.0', str(book_data[field]) if book_data[field] else '')
            else:
                entry = tk.Entry(edit_window, font=('Arial', 12), width=30)
                entry.insert(0, str(book_data[field]) if book_data[field] else '')
            
            entry.grid(row=i, column=1, padx=20, pady=10)
            entries[field] = entry
        
        def update_book():
            try:
                values = {}
                for field, entry in entries.items():
                    if field == 'Description':
                        values[field] = entry.get('1.0', tk.END).strip()
                    else:
                        values[field] = entry.get()
                
                # Calculate available copies change
                old_total = book[7]
                new_total = int(values['Total Copies'])
                available_change = new_total - old_total
                new_available = book[8] + available_change
                
                self.cursor.execute('''
                    UPDATE books SET isbn=?, title=?, author=?, category=?, publisher=?,
                                   publication_year=?, total_copies=?, available_copies=?,
                                   location=?, price=?, description=?
                    WHERE id=?
                ''', (values['ISBN'], values['Title'], values['Author'], values['Category'],
                      values['Publisher'], int(values['Publication Year']), new_total,
                      new_available, values['Location'], float(values['Price']),
                      values['Description'], book_id))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Book updated successfully!")
                edit_window.destroy()
                self.load_books()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update book: {str(e)}")
        
        tk.Button(edit_window, text="Update Book", command=update_book,
                 bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                 padx=30, pady=10).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def delete_book(self):
        """Delete selected book"""
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to delete!")
            return
        
        book_id = self.books_tree.item(selected[0])['values'][0]
        
        # Check if book is currently borrowed
        self.cursor.execute('SELECT COUNT(*) FROM transactions WHERE book_id = ? AND status = "active"', 
                           (book_id,))
        active_loans = self.cursor.fetchone()[0]
        
        if active_loans > 0:
            messagebox.showerror("Error", "Cannot delete book with active loans!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this book?"):
            self.cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Book deleted successfully!")
            self.load_books()
    
    def view_book_details(self):
        """View detailed book information"""
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book!")
            return
        
        book_id = self.books_tree.item(selected[0])['values'][0]
        
        self.cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        book = self.cursor.fetchone()
        
        # Get reviews for this book
        self.cursor.execute('''
            SELECT u.full_name, r.rating, r.review_text, r.review_date
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.book_id = ?
            ORDER BY r.review_date DESC
        ''', (book_id,))
        reviews = self.cursor.fetchall()
        
        details_window = tk.Toplevel(self.root)
        details_window.title("Book Details")
        details_window.geometry("600x800")
        details_window.configure(bg='#ecf0f1')
        
        # Book information
        info_frame = tk.LabelFrame(details_window, text="Book Information", 
                                  font=('Arial', 14, 'bold'))
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        book_info = [
            ("Title:", book[2]),
            ("Author:", book[3]),
            ("ISBN:", book[1]),
            ("Category:", book[4]),
            ("Publisher:", book[5]),
            ("Publication Year:", book[6]),
            ("Total Copies:", book[7]),
            ("Available Copies:", book[8]),
            ("Location:", book[9]),
            ("Price:", f"${book[12]:.2f}" if book[12] else "N/A"),
            ("Added Date:", book[11]),
            ("Description:", book[10])
        ]
        
        for i, (label, value) in enumerate(book_info):
            tk.Label(info_frame, text=label, font=('Arial', 10, 'bold'),
                    bg='#ecf0f1').grid(row=i, column=0, padx=10, pady=5, sticky='w')
            
            if label == "Description:":
                desc_text = tk.Text(info_frame, height=4, width=50, wrap=tk.WORD)
                desc_text.insert('1.0', str(value) if value else "No description available")
                desc_text.configure(state='disabled')
                desc_text.grid(row=i, column=1, padx=10, pady=5, sticky='w')
            else:
                tk.Label(info_frame, text=str(value) if value else "N/A",
                        bg='#ecf0f1').grid(row=i, column=1, padx=10, pady=5, sticky='w')
        
        # Reviews section
        reviews_frame = tk.LabelFrame(details_window, text="Reviews", 
                                     font=('Arial', 14, 'bold'))
        reviews_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        reviews_text = tk.Text(reviews_frame, wrap=tk.WORD)
        reviews_scrollbar = tk.Scrollbar(reviews_frame, orient="vertical", command=reviews_text.yview)
        reviews_text.configure(yscrollcommand=reviews_scrollbar.set)
        
        reviews_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        reviews_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        if reviews:
            for review in reviews:
                reviews_text.insert(tk.END, f"★" * review[1] + "☆" * (5 - review[1]) + f" - {review[0]}\n")
                reviews_text.insert(tk.END, f"Date: {review[3]}\n")
                reviews_text.insert(tk.END, f"{review[2]}\n")
                reviews_text.insert(tk.END, "-" * 50 + "\n\n")
        else:
            reviews_text.insert(tk.END, "No reviews available for this book.")
        
        reviews_text.configure(state='disabled')
    
    def add_book_review(self):
        """Add review for selected book"""
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book!")
            return
        
        if self.user_role != 'member':
            messagebox.showinfo("Info", "Only members can add reviews!")
            return
        
        book_id = self.books_tree.item(selected[0])['values'][0]
        
        review_window = tk.Toplevel(self.root)
        review_window.title("Add Review")
        review_window.geometry("400x300")
        review_window.configure(bg='#ecf0f1')
        
        tk.Label(review_window, text="Rating (1-5):", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=10)
        rating_var = tk.IntVar(value=5)
        rating_frame = tk.Frame(review_window, bg='#ecf0f1')
        rating_frame.pack()
        
        for i in range(1, 6):
            tk.Radiobutton(rating_frame, text=f"{i}★", variable=rating_var, value=i,
                          bg='#ecf0f1').pack(side=tk.LEFT)
        
        tk.Label(review_window, text="Review:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=(20, 5))
        review_text = tk.Text(review_window, height=8, width=40)
        review_text.pack(pady=5)
        
        def save_review():
            try:
                self.cursor.execute('''
                    INSERT INTO reviews (user_id, book_id, rating, review_text, review_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.current_user[0], book_id, rating_var.get(),
                      review_text.get('1.0', tk.END).strip(),
                      datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Review added successfully!")
                review_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add review: {str(e)}")
        
        tk.Button(review_window, text="Save Review", command=save_review,
                 bg='#3498db', fg='white', padx=20, pady=10).pack(pady=20)
    
    def show_books_context_menu(self, event):
        """Show context menu for books"""
        try:
            self.books_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.books_context_menu.grab_release()
    
    def search_members(self, event=None):
        """Search members based on query"""
        query = self.member_search_entry.get()
        if query:
            self.cursor.execute('''
                SELECT id, username, full_name, email, phone, membership_status, fine_balance
                FROM users 
                WHERE role = 'member' AND (username LIKE ? OR full_name LIKE ? OR email LIKE ?)
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        else:
            self.cursor.execute('''
                SELECT id, username, full_name, email, phone, membership_status, fine_balance
                FROM users WHERE role = 'member'
            ''')
        
        members = self.cursor.fetchall()
        self.update_members_tree(members)
    
    def update_members_tree(self, members):
        """Update members treeview with data"""
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        for member in members:
            self.members_tree.insert('', 'end', values=member)
    
    def load_members(self):
        """Load all members into treeview"""
        self.cursor.execute('''
            SELECT id, username, full_name, email, phone, membership_status, fine_balance
            FROM users WHERE role = 'member'
        ''')
        members = self.cursor.fetchall()
        self.update_members_tree(members)
    
    def edit_member(self):
        """Edit selected member"""
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member to edit!")
            return
        
        member_id = self.members_tree.item(selected[0])['values'][0]
        
        # Get member details
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (member_id,))
        member = self.cursor.fetchone()
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Member")
        edit_window.geometry("500x600")
        edit_window.configure(bg='#ecf0f1')
        
        fields = ['Username', 'Full Name', 'Email', 'Phone', 'Address']
        entries = {}
        
        # Pre-fill with existing data
        member_data = {
            'Username': member[1], 'Full Name': member[4], 'Email': member[5],
            'Phone': member[6], 'Address': member[7]
        }
        
        for i, field in enumerate(fields):
            tk.Label(edit_window, text=f"{field}:", font=('Arial', 12),
                    bg='#ecf0f1').grid(row=i, column=0, padx=20, pady=10, sticky='w')
            
            entry = tk.Entry(edit_window, font=('Arial', 12), width=30)
            entry.insert(0, str(member_data[field]) if member_data[field] else '')
            entry.grid(row=i, column=1, padx=20, pady=10)
            entries[field] = entry
        
        # Membership status
        tk.Label(edit_window, text="Status:", font=('Arial', 12),
                bg='#ecf0f1').grid(row=len(fields), column=0, padx=20, pady=10, sticky='w')
        status_var = tk.StringVar(value=member[9])
        status_combo = ttk.Combobox(edit_window, textvariable=status_var,
                                   values=['active', 'suspended', 'inactive'])
        status_combo.grid(row=len(fields), column=1, padx=20, pady=10)
        
        def update_member():
            try:
                values = {field: entry.get() for field, entry in entries.items()}
                
                self.cursor.execute('''
                    UPDATE users SET username=?, full_name=?, email=?, phone=?, 
                                   address=?, membership_status=?
                    WHERE id=?
                ''', (values['Username'], values['Full Name'], values['Email'],
                      values['Phone'], values['Address'], status_var.get(), member_id))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Member updated successfully!")
                edit_window.destroy()
                self.load_members()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update member: {str(e)}")
        
        tk.Button(edit_window, text="Update Member", command=update_member,
                 bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                 padx=30, pady=10).grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
    
    def view_member_history(self):
        """View member's borrowing history"""
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member!")
            return
        
        member_id = self.members_tree.item(selected[0])['values'][0]
        
        # Get member info
        self.cursor.execute('SELECT full_name FROM users WHERE id = ?', (member_id,))
        member_name = self.cursor.fetchone()[0]
        
        # Get transaction history
        self.cursor.execute('''
            SELECT b.title, t.transaction_type, t.issue_date, t.due_date, 
                   t.return_date, t.fine_amount, t.status
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            WHERE t.user_id = ?
            ORDER BY t.issue_date DESC
        ''', (member_id,))
        history = self.cursor.fetchall()
        
        history_window = tk.Toplevel(self.root)
        history_window.title(f"Transaction History - {member_name}")
        history_window.geometry("800x600")
        history_window.configure(bg='#ecf0f1')
        
        # History treeview
        columns = ('Book Title', 'Type', 'Issue Date', 'Due Date', 'Return Date', 'Fine', 'Status')
        history_tree = ttk.Treeview(history_window, columns=columns, show='headings')
        
        for col in columns:
            history_tree.heading(col, text=col)
            history_tree.column(col, width=100)
        
        history_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        for transaction in history:
            history_tree.insert('', 'end', values=transaction)
    
    def suspend_member(self):
        """Suspend selected member"""
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member!")
            return
        
        member_id = self.members_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to suspend this member?"):
            self.cursor.execute('UPDATE users SET membership_status = "suspended" WHERE id = ?',
                               (member_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Member suspended successfully!")
            self.load_members()
    
    def send_message_to_member(self):
        """Send message to selected member"""
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member!")
            return
        
        member_id = self.members_tree.item(selected[0])['values'][0]
        
        # Get member email
        self.cursor.execute('SELECT email, full_name FROM users WHERE id = ?', (member_id,))
        member_info = self.cursor.fetchone()
        
        message_window = tk.Toplevel(self.root)
        message_window.title(f"Send Message to {member_info[1]}")
        message_window.geometry("500x400")
        message_window.configure(bg='#ecf0f1')
        
        tk.Label(message_window, text=f"To: {member_info[1]} ({member_info[0]})",
                font=('Arial', 12), bg='#ecf0f1').pack(pady=10)
        
        tk.Label(message_window, text="Subject:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=(10, 0))
        subject_entry = tk.Entry(message_window, font=('Arial', 12), width=50)
        subject_entry.pack(pady=5)
        
        tk.Label(message_window, text="Message:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=(10, 0))
        message_text = tk.Text(message_window, height=12, width=50)
        message_text.pack(pady=5)
        
        def send_message():
            messagebox.showinfo("Message Sent", 
                              f"Message sent to {member_info[1]}\n"
                              f"Subject: {subject_entry.get()}\n"
                              "Note: This is a demo - no actual email sent.")
            message_window.destroy()
        
        tk.Button(message_window, text="Send Message", command=send_message,
                 bg='#3498db', fg='white', padx=20, pady=10).pack(pady=20)
    
    def show_members_context_menu(self, event):
        """Show context menu for members"""
        try:
            self.members_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.members_context_menu.grab_release()
    
    def load_transactions(self):
        """Load all transactions into treeview"""
        self.cursor.execute('''
            SELECT t.id, u.full_name, b.title, t.transaction_type, 
                   t.issue_date, t.due_date, t.status, t.fine_amount
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            JOIN books b ON t.book_id = b.id
            ORDER BY t.issue_date DESC
        ''')
        transactions = self.cursor.fetchall()
        
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        for transaction in transactions:
            self.transactions_tree.insert('', 'end', values=transaction)
    
    def issue_book(self):
        """Issue book to member"""
        issue_window = tk.Toplevel(self.root)
        issue_window.title("Issue Book")
        issue_window.geometry("400x300")
        issue_window.configure(bg='#ecf0f1')
        
        tk.Label(issue_window, text="Member ID or Username:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=10)
        member_entry = tk.Entry(issue_window, font=('Arial', 12), width=30)
        member_entry.pack(pady=5)
        
        tk.Label(issue_window, text="Book ID or ISBN:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=10)
        book_entry = tk.Entry(issue_window, font=('Arial', 12), width=30)
        book_entry.pack(pady=5)
        
        tk.Label(issue_window, text="Loan Period (days):", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=10)
        period_var = tk.StringVar(value="14")
        period_entry = tk.Entry(issue_window, textvariable=period_var, font=('Arial', 12), width=30)
        period_entry.pack(pady=5)
        
        def process_issue():
            try:
                # Find member
                member_input = member_entry.get()
                self.cursor.execute('''
                    SELECT id, membership_status FROM users 
                    WHERE (id = ? OR username = ?) AND role = 'member'
                ''', (member_input, member_input))
                member = self.cursor.fetchone()
                
                if not member:
                    messagebox.showerror("Error", "Member not found!")
                    return
                
                if member[1] == 'suspended':
                    messagebox.showerror("Error", "Member is suspended!")
                    return
                
                # Find book
                book_input = book_entry.get()
                self.cursor.execute('''
                    SELECT id, title, available_copies FROM books 
                    WHERE id = ? OR isbn = ?
                ''', (book_input, book_input))
                book = self.cursor.fetchone()
                
                if not book:
                    messagebox.showerror("Error", "Book not found!")
                    return
                
                if book[2] <= 0:
                    messagebox.showerror("Error", "Book not available!")
                    return
                
                # Create transaction
                issue_date = datetime.datetime.now()
                due_date = issue_date + datetime.timedelta(days=int(period_var.get()))
                
                self.cursor.execute('''
                    INSERT INTO transactions (user_id, book_id, transaction_type, 
                                            issue_date, due_date, status)
                    VALUES (?, ?, 'issue', ?, ?, 'active')
                ''', (member[0], book[0], issue_date.strftime("%Y-%m-%d"),
                      due_date.strftime("%Y-%m-%d")))
                
                # Update book availability
                self.cursor.execute('''
                    UPDATE books SET available_copies = available_copies - 1 
                    WHERE id = ?
                ''', (book[0],))
                
                self.conn.commit()
                messagebox.showinfo("Success", f"Book '{book[1]}' issued successfully!")
                issue_window.destroy()
                self.load_transactions()
                self.load_books()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to issue book: {str(e)}")
        
        tk.Button(issue_window, text="Issue Book", command=process_issue,
                 bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                 padx=30, pady=10).pack(pady=20)
    
    def return_book(self):
        """Return book from member"""
        return_window = tk.Toplevel(self.root)
        return_window.title("Return Book")
        return_window.geometry("400x200")
        return_window.configure(bg='#ecf0f1')
        
        tk.Label(return_window, text="Transaction ID:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=20)
        transaction_entry = tk.Entry(return_window, font=('Arial', 12), width=30)
        transaction_entry.pack(pady=5)
        
        def process_return():
            try:
                transaction_id = transaction_entry.get()
                
                # Get transaction details
                self.cursor.execute('''
                    SELECT t.*, b.title, u.full_name FROM transactions t
                    JOIN books b ON t.book_id = b.id
                    JOIN users u ON t.user_id = u.id
                    WHERE t.id = ? AND t.status = 'active'
                ''', (transaction_id,))
                transaction = self.cursor.fetchone()
                
                if not transaction:
                    messagebox.showerror("Error", "Active transaction not found!")
                    return
                
                # Calculate fine if overdue
                return_date = datetime.datetime.now()
                due_date = datetime.datetime.strptime(transaction[5], "%Y-%m-%d")
                fine_amount = 0.0
                
                if return_date.date() > due_date.date():
                    days_overdue = (return_date.date() - due_date.date()).days
                    fine_amount = days_overdue * float(self.fine_per_day_var.get())
                
                # Update transaction
                self.cursor.execute('''
                    UPDATE transactions SET return_date = ?, fine_amount = ?, status = 'returned'
                    WHERE id = ?
                ''', (return_date.strftime("%Y-%m-%d"), fine_amount, transaction_id))
                
                # Update book availability
                self.cursor.execute('''
                    UPDATE books SET available_copies = available_copies + 1 
                    WHERE id = ?
                ''', (transaction[2],))
                
                # Add fine to user balance
                if fine_amount > 0:
                    self.cursor.execute('''
                        UPDATE users SET fine_balance = fine_balance + ? 
                        WHERE id = ?
                    ''', (fine_amount, transaction[1]))
                
                self.conn.commit()
                
                message = f"Book '{transaction[8]}' returned successfully!"
                if fine_amount > 0:
                    message += f"\nFine: ${fine_amount:.2f}"
                
                messagebox.showinfo("Success", message)
                return_window.destroy()
                self.load_transactions()
                self.load_books()
                self.load_members()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to return book: {str(e)}")
        
        tk.Button(return_window, text="Return Book", command=process_return,
                 bg='#2ecc71', fg='white', font=('Arial', 12, 'bold'),
                 padx=30, pady=10).pack(pady=20)
    
    def renew_book(self):
        """Renew book loan"""
        renew_window = tk.Toplevel(self.root)
        renew_window.title("Renew Book")
        renew_window.geometry("400x200")
        renew_window.configure(bg='#ecf0f1')
        
        tk.Label(renew_window, text="Transaction ID:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=20)
        transaction_entry = tk.Entry(renew_window, font=('Arial', 12), width=30)
        transaction_entry.pack(pady=5)
        
        def process_renewal():
            try:
                transaction_id = transaction_entry.get()
                
                # Get transaction details
                self.cursor.execute('''
                    SELECT * FROM transactions WHERE id = ? AND status = 'active'
                ''', (transaction_id,))
                transaction = self.cursor.fetchone()
                
                if not transaction:
                    messagebox.showerror("Error", "Active transaction not found!")
                    return
                
                # Extend due date by default loan period
                current_due = datetime.datetime.strptime(transaction[5], "%Y-%m-%d")
                new_due = current_due + datetime.timedelta(days=int(self.loan_period_var.get()))
                
                self.cursor.execute('''
                    UPDATE transactions SET due_date = ? WHERE id = ?
                ''', (new_due.strftime("%Y-%m-%d"), transaction_id))
                
                self.conn.commit()
                messagebox.showinfo("Success", f"Book renewed! New due date: {new_due.strftime('%Y-%m-%d')}")
                renew_window.destroy()
                self.load_transactions()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to renew book: {str(e)}")
        
        tk.Button(renew_window, text="Renew Book", command=process_renewal,
                 bg='#f39c12', fg='white', font=('Arial', 12, 'bold'),
                 padx=30, pady=10).pack(pady=20)
    
    def reserve_book(self):
        """Reserve book for member"""
        reserve_window = tk.Toplevel(self.root)
        reserve_window.title("Reserve Book")
        reserve_window.geometry("400x250")
        reserve_window.configure(bg='#ecf0f1')
        
        tk.Label(reserve_window, text="Member ID or Username:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=10)
        member_entry = tk.Entry(reserve_window, font=('Arial', 12), width=30)
        member_entry.pack(pady=5)
        
        tk.Label(reserve_window, text="Book ID or ISBN:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=10)
        book_entry = tk.Entry(reserve_window, font=('Arial', 12), width=30)
        book_entry.pack(pady=5)
        
        def process_reservation():
            try:
                # Find member
                member_input = member_entry.get()
                self.cursor.execute('''
                    SELECT id FROM users WHERE (id = ? OR username = ?) AND role = 'member'
                ''', (member_input, member_input))
                member = self.cursor.fetchone()
                
                if not member:
                    messagebox.showerror("Error", "Member not found!")
                    return
                
                # Find book
                book_input = book_entry.get()
                self.cursor.execute('SELECT id FROM books WHERE id = ? OR isbn = ?', 
                                   (book_input, book_input))
                book = self.cursor.fetchone()
                
                if not book:
                    messagebox.showerror("Error", "Book not found!")
                    return
                
                # Create reservation
                self.cursor.execute('''
                    INSERT INTO reservations (user_id, book_id, reservation_date, status)
                    VALUES (?, ?, ?, 'active')
                ''', (member[0], book[0], datetime.datetime.now().strftime("%Y-%m-%d")))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Book reserved successfully!")
                reserve_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reserve book: {str(e)}")
        
        tk.Button(reserve_window, text="Reserve Book", command=process_reservation,
                 bg='#9b59b6', fg='white', font=('Arial', 12, 'bold'),
                 padx=30, pady=10).pack(pady=20)
    
    # Report generation methods
    def generate_overdue_report(self):
        """Generate overdue books report"""
        self.cursor.execute('''
            SELECT u.full_name, b.title, t.issue_date, t.due_date, 
                   julianday('now') - julianday(t.due_date) as days_overdue
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            JOIN books b ON t.book_id = b.id
            WHERE t.status = 'active' AND date(t.due_date) < date('now')
            ORDER BY days_overdue DESC
        ''')
        overdue_books = self.cursor.fetchall()
        
        report = "OVERDUE BOOKS REPORT\n"
        report += "=" * 50 + "\n\n"
        report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total overdue books: {len(overdue_books)}\n\n"
        
        if overdue_books:
            report += f"{'Member':<20} {'Book Title':<30} {'Issue Date':<12} {'Due Date':<12} {'Days Overdue':<12}\n"
            report += "-" * 100 + "\n"
            
            for book in overdue_books:
                report += f"{book[0]:<20} {book[1][:28]:<30} {book[2]:<12} {book[3]:<12} {int(book[4]):<12}\n"
        else:
            report += "No overdue books found!\n"
        
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert('1.0', report)
    
    def generate_popular_books_report(self):
        """Generate popular books report"""
        self.cursor.execute('''
            SELECT b.title, b.author, COUNT(t.id) as loan_count,
                   AVG(r.rating) as avg_rating
            FROM books b
            LEFT JOIN transactions t ON b.id = t.book_id
            LEFT JOIN reviews r ON b.id = r.book_id
            GROUP BY b.id
            ORDER BY loan_count DESC, avg_rating DESC
            LIMIT 20
        ''')
        popular_books = self.cursor.fetchall()
        
        report = "POPULAR BOOKS REPORT\n"
        report += "=" * 50 + "\n\n"
        report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "Top 20 most borrowed books:\n\n"
        
        report += f"{'Rank':<5} {'Title':<30} {'Author':<20} {'Loans':<8} {'Avg Rating':<10}\n"
        report += "-" * 80 + "\n"
        
        for i, book in enumerate(popular_books, 1):
            avg_rating = f"{book[3]:.1f}★" if book[3] else "No ratings"
            report += f"{i:<5} {book[0][:28]:<30} {book[1][:18]:<20} {book[2]:<8} {avg_rating:<10}\n"
        
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert('1.0', report)
    
    def generate_member_activity_report(self):
        """Generate member activity report"""
        self.cursor.execute('''
            SELECT u.full_name, u.email, 
                   COUNT(t.id) as total_loans,
                   MAX(t.issue_date) as last_loan,
                   u.fine_balance,
                   u.membership_status
            FROM users u
            LEFT JOIN transactions t ON u.id = t.user_id
            WHERE u.role = 'member'
            GROUP BY u.id
            ORDER BY total_loans DESC
        ''')
        member_activity = self.cursor.fetchall()
        
        report = "MEMBER ACTIVITY REPORT\n"
        report += "=" * 60 + "\n\n"
        report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total members: {len(member_activity)}\n\n"
        
        report += f"{'Name':<20} {'Email':<25} {'Loans':<8} {'Last Loan':<12} {'Fine':<10} {'Status':<10}\n"
        report += "-" * 90 + "\n"
        
        for member in member_activity:
            last_loan = member[3] if member[3] else "Never"
            report += f"{member[0][:18]:<20} {member[1][:23]:<25} {member[2]:<8} {last_loan:<12} ${member[4]:<9.2f} {member[5]:<10}\n"
        
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert('1.0', report)
    
    def generate_financial_report(self):
        """Generate financial report"""
        # Get total fines collected
        self.cursor.execute('SELECT SUM(fine_amount) FROM transactions WHERE fine_amount > 0')
        total_fines_collected = self.cursor.fetchone()[0] or 0
        
        # Get outstanding fines
        self.cursor.execute('SELECT SUM(fine_balance) FROM users WHERE fine_balance > 0')
        outstanding_fines = self.cursor.fetchone()[0] or 0
        
        # Get monthly fine collection
        self.cursor.execute('''
            SELECT strftime('%Y-%m', return_date) as month, SUM(fine_amount) as monthly_fines
            FROM transactions 
            WHERE return_date IS NOT NULL AND fine_amount > 0
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        ''')
        monthly_fines = self.cursor.fetchall()
        
        report = "FINANCIAL REPORT\n"
        report += "=" * 40 + "\n\n"
        report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "SUMMARY:\n"
        report += f"Total fines collected: ${total_fines_collected:.2f}\n"
        report += f"Outstanding fines: ${outstanding_fines:.2f}\n"
        report += f"Total revenue: ${total_fines_collected:.2f}\n\n"
        
        report += "MONTHLY FINE COLLECTION (Last 12 months):\n"
        report += "-" * 30 + "\n"
        
        for month_data in monthly_fines:
            report += f"{month_data[0]}: ${month_data[1]:.2f}\n"
        
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert('1.0', report)
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        self.cursor.execute('''
            SELECT category, COUNT(*) as book_count, SUM(total_copies) as total_copies,
                   SUM(available_copies) as available_copies
            FROM books
            GROUP BY category
            ORDER BY book_count DESC
        ''')
        inventory_by_category = self.cursor.fetchall()
        
        self.cursor.execute('''
            SELECT COUNT(*) as total_books, SUM(total_copies) as total_copies,
                   SUM(available_copies) as available_copies
            FROM books
        ''')
        totals = self.cursor.fetchone()
        
        report = "INVENTORY REPORT\n"
        report += "=" * 50 + "\n\n"
        report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "OVERALL SUMMARY:\n"
        report += f"Total unique books: {totals[0]}\n"
        report += f"Total copies: {totals[1]}\n"
        report += f"Available copies: {totals[2]}\n"
        report += f"Borrowed copies: {totals[1] - totals[2]}\n"
        report += f"Availability rate: {(totals[2]/totals[1]*100):.1f}%\n\n"
        
        report += "INVENTORY BY CATEGORY:\n"
        report += "-" * 40 + "\n"
        report += f"{'Category':<15} {'Books':<8} {'Total':<8} {'Available':<10} {'Rate':<8}\n"
        report += "-" * 50 + "\n"
        
        for category in inventory_by_category:
            rate = (category[3] / category[2] * 100) if category[2] > 0 else 0
            category_name = category[0] if category[0] else "Uncategorized"
            report += f"{category_name[:13]:<15} {category[1]:<8} {category[2]:<8} {category[3]:<10} {rate:.1f}%\n"
        
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert('1.0', report)
    
    def create_custom_report(self):
        """Create custom report with user-defined criteria"""
        custom_window = tk.Toplevel(self.root)
        custom_window.title("Custom Report Builder")
        custom_window.geometry("600x500")
        custom_window.configure(bg='#ecf0f1')
        
        tk.Label(custom_window, text="Custom Report Builder", font=('Arial', 16, 'bold'),
                bg='#ecf0f1').pack(pady=20)
        
        # Report type selection
        tk.Label(custom_window, text="Select Report Type:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=10)
        
        report_type = tk.StringVar(value="transactions")
        report_types = [
            ("Transaction Report", "transactions"),
            ("Member Report", "members"),
            ("Book Report", "books"),
            ("Fine Report", "fines")
        ]
        
        for text, value in report_types:
            tk.Radiobutton(custom_window, text=text, variable=report_type, value=value,
                          bg='#ecf0f1').pack()
        
        # Date range
        date_frame = tk.Frame(custom_window, bg='#ecf0f1')
        date_frame.pack(pady=20)
        
        tk.Label(date_frame, text="Date Range:", font=('Arial', 12),
                bg='#ecf0f1').pack()
        
        tk.Label(date_frame, text="From:", bg='#ecf0f1').pack(side=tk.LEFT)
        from_date = tk.Entry(date_frame, width=12)
        from_date.insert(0, "2024-01-01")
        from_date.pack(side=tk.LEFT, padx=5)
        
        tk.Label(date_frame, text="To:", bg='#ecf0f1').pack(side=tk.LEFT)
        to_date = tk.Entry(date_frame, width=12)
        to_date.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        to_date.pack(side=tk.LEFT, padx=5)
        
        def generate_custom_report():
            report_type_val = report_type.get()
            from_date_val = from_date.get()
            to_date_val = to_date.get()
            
            report = f"CUSTOM {report_type_val.upper()} REPORT\n"
            report += "=" * 50 + "\n\n"
            report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"Date range: {from_date_val} to {to_date_val}\n\n"
            
            if report_type_val == "transactions":
                self.cursor.execute('''
                    SELECT u.full_name, b.title, t.transaction_type, t.issue_date, 
                           t.due_date, t.return_date, t.fine_amount
                    FROM transactions t
                    JOIN users u ON t.user_id = u.id
                    JOIN books b ON t.book_id = b.id
                    WHERE t.issue_date BETWEEN ? AND ?
                    ORDER BY t.issue_date DESC
                ''', (from_date_val, to_date_val))
                data = self.cursor.fetchall()
                
                report += f"{'Member':<20} {'Book':<25} {'Type':<10} {'Issue':<12} {'Due':<12} {'Return':<12} {'Fine':<8}\n"
                report += "-" * 110 + "\n"
                
                for row in data:
                    return_date = row[5] if row[5] else "Active"
                    report += f"{row[0][:18]:<20} {row[1][:23]:<25} {row[2]:<10} {row[3]:<12} {row[4]:<12} {return_date:<12} ${row[6]:<7.2f}\n"
            
            elif report_type_val == "members":
                self.cursor.execute('''
                    SELECT full_name, email, registration_date, membership_status, fine_balance
                    FROM users
                    WHERE role = 'member' AND registration_date BETWEEN ? AND ?
                    ORDER BY registration_date DESC
                ''', (from_date_val, to_date_val))
                data = self.cursor.fetchall()
                
                report += f"{'Name':<25} {'Email':<30} {'Registration':<15} {'Status':<12} {'Fine':<10}\n"
                report += "-" * 95 + "\n"
                
                for row in data:
                    report += f"{row[0][:23]:<25} {row[1][:28]:<30} {row[2]:<15} {row[3]:<12} ${row[4]:<9.2f}\n"
            
            elif report_type_val == "books":
                self.cursor.execute('''
                    SELECT title, author, category, total_copies, available_copies, added_date
                    FROM books
                    WHERE added_date BETWEEN ? AND ?
                    ORDER BY added_date DESC
                ''', (from_date_val, to_date_val))
                data = self.cursor.fetchall()
                
                report += f"{'Title':<30} {'Author':<20} {'Category':<15} {'Total':<8} {'Available':<10} {'Added':<12}\n"
                report += "-" * 100 + "\n"
                
                for row in data:
                    report += f"{row[0][:28]:<30} {row[1][:18]:<20} {row[2][:13]:<15} {row[3]:<8} {row[4]:<10} {row[5]:<12}\n"
            
            self.report_text.delete('1.0', tk.END)
            self.report_text.insert('1.0', report)
            custom_window.destroy()
        
        tk.Button(custom_window, text="Generate Report", command=generate_custom_report,
                 bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                 padx=30, pady=10).pack(pady=30)
    
    # Utility methods
    def import_books(self):
        """Import books from CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                imported_count = 0
                with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            self.cursor.execute('''
                                INSERT INTO books (isbn, title, author, category, publisher,
                                                 publication_year, total_copies, available_copies,
                                                 location, price, description, added_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (row.get('ISBN', ''), row.get('Title', ''), row.get('Author', ''),
                                  row.get('Category', ''), row.get('Publisher', ''),
                                  int(row.get('Year', 0)), int(row.get('Copies', 1)),
                                  int(row.get('Copies', 1)), row.get('Location', ''),
                                  float(row.get('Price', 0)), row.get('Description', ''),
                                  datetime.datetime.now().strftime("%Y-%m-%d")))
                            imported_count += 1
                        except Exception as e:
                            print(f"Error importing row: {e}")
                            continue
                
                self.conn.commit()
                messagebox.showinfo("Success", f"Imported {imported_count} books successfully!")
                self.load_books()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import books: {str(e)}")
    
    def export_data(self):
        """Export data to various formats"""
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Data")
        export_window.geometry("300x200")
        export_window.configure(bg='#ecf0f1')
        
        tk.Label(export_window, text="Select data to export:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=20)
        
        export_options = ["Books", "Members", "Transactions", "All Data"]
        selected_option = tk.StringVar(value="Books")
        
        for option in export_options:
            tk.Radiobutton(export_window, text=option, variable=selected_option,
                          value=option, bg='#ecf0f1').pack()
        
        def perform_export():
            option = selected_option.get()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")]
            )
            
            if file_path:
                try:
                    if option == "Books":
                        self.cursor.execute('SELECT * FROM books')
                        data = self.cursor.fetchall()
                        headers = [desc[0] for desc in self.cursor.description]
                    elif option == "Members":
                        self.cursor.execute('SELECT * FROM users WHERE role = "member"')
                        data = self.cursor.fetchall()
                        headers = [desc[0] for desc in self.cursor.description]
                    elif option == "Transactions":
                        self.cursor.execute('''
                            SELECT t.*, u.full_name, b.title 
                            FROM transactions t
                            JOIN users u ON t.user_id = u.id
                            JOIN books b ON t.book_id = b.id
                        ''')
                        data = self.cursor.fetchall()
                        headers = [desc[0] for desc in self.cursor.description]
                    
                    if file_path.endswith('.csv'):
                        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(headers)
                            writer.writerows(data)
                    elif file_path.endswith('.json'):
                        json_data = [dict(zip(headers, row)) for row in data]
                        with open(file_path, 'w', encoding='utf-8') as jsonfile:
                            json.dump(json_data, jsonfile, indent=2, default=str)
                    
                    messagebox.showinfo("Success", f"Data exported to {file_path}")
                    export_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Export failed: {str(e)}")
        
        tk.Button(export_window, text="Export", command=perform_export,
                 bg='#3498db', fg='white', padx=20, pady=10).pack(pady=20)
    
    def backup_database(self):
        """Backup database to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("SQL files", "*.sql")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.sql'):
                    with open(file_path, 'w') as f:
                        for line in self.conn.iterdump():
                            f.write('%s\n' % line)
                else:
                    import shutil
                    shutil.copy2('library_system.db', file_path)
                
                messagebox.showinfo("Success", f"Database backed up to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def restore_database(self):
        """Restore database from backup"""
        file_path = filedialog.askopenfilename(
            title="Select backup file",
            filetypes=[("Database files", "*.db"), ("SQL files", "*.sql")]
        )
        
        if file_path:
            if messagebox.askyesno("Confirm", "This will replace current data. Continue?"):
                try:
                    if file_path.endswith('.sql'):
                        # Clear current database
                        self.cursor.executescript('''
                            DROP TABLE IF EXISTS books;
                            DROP TABLE IF EXISTS users;
                            DROP TABLE IF EXISTS transactions;
                            DROP TABLE IF EXISTS reservations;
                            DROP TABLE IF EXISTS reviews;
                        ''')
                        
                        # Execute SQL backup
                        with open(file_path, 'r') as f:
                            self.cursor.executescript(f.read())
                    else:
                        self.conn.close()
                        import shutil
                        shutil.copy2(file_path, 'library_system.db')
                        self.conn = sqlite3.connect('library_system.db')
                        self.cursor = self.conn.cursor()
                    
                    messagebox.showinfo("Success", "Database restored successfully!")
                    self.load_books()
                    self.load_members()
                    self.load_transactions()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Restore failed: {str(e)}")
    
    def send_notifications(self):
        """Send automated notifications"""
        # Get overdue books
        self.cursor.execute('''
            SELECT u.full_name, u.email, b.title, t.due_date
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            JOIN books b ON t.book_id = b.id
            WHERE t.status = 'active' AND date(t.due_date) < date('now')
        ''')
        overdue_books = self.cursor.fetchall()
        
        # Get books due soon
        self.cursor.execute('''
            SELECT u.full_name, u.email, b.title, t.due_date
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            JOIN books b ON t.book_id = b.id
            WHERE t.status = 'active' AND date(t.due_date) BETWEEN date('now') AND date('now', '+3 days')
        ''')
        due_soon_books = self.cursor.fetchall()
        
        notification_text = f"NOTIFICATION SUMMARY\n"
        notification_text += "=" * 30 + "\n\n"
        notification_text += f"Overdue notifications: {len(overdue_books)}\n"
        notification_text += f"Due soon notifications: {len(due_soon_books)}\n\n"
        
        notification_text += "OVERDUE BOOKS:\n"
        for book in overdue_books:
            notification_text += f"- {book[0]} ({book[1]}): '{book[2]}' due {book[3]}\n"
        
        notification_text += "\nDUE SOON:\n"
        for book in due_soon_books:
            notification_text += f"- {book[0]} ({book[1]}): '{book[2]}' due {book[3]}\n"
        
        notification_text += "\nNote: In a real system, these would be sent as emails/SMS."
        
        # Show notification window
        notif_window = tk.Toplevel(self.root)
        notif_window.title("Notification Summary")
        notif_window.geometry("600x400")
        
        text_widget = tk.Text(notif_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert('1.0', notification_text)
        text_widget.configure(state='disabled')
        
        messagebox.showinfo("Notifications Sent", 
                           f"Sent {len(overdue_books) + len(due_soon_books)} notifications!")
    
    def calculate_fines(self):
        """Calculate and update fines for overdue books"""
        self.cursor.execute('''
            SELECT t.id, t.user_id, t.due_date, julianday('now') - julianday(t.due_date) as days_overdue
            FROM transactions t
            WHERE t.status = 'active' AND date(t.due_date) < date('now')
        ''')
        overdue_transactions = self.cursor.fetchall()
        
        total_fines = 0
        fine_per_day = float(self.fine_per_day_var.get())
        
        for transaction in overdue_transactions:
            days_overdue = max(0, int(transaction[3]))
            fine_amount = days_overdue * fine_per_day
            
            # Update transaction fine
            self.cursor.execute('''
                UPDATE transactions SET fine_amount = ? WHERE id = ?
            ''', (fine_amount, transaction[0]))
            
            # Update user fine balance
            self.cursor.execute('''
                UPDATE users SET fine_balance = fine_balance + ? WHERE id = ?
            ''', (fine_amount, transaction[1]))
            
            total_fines += fine_amount
        
        self.conn.commit()
        messagebox.showinfo("Fines Calculated", 
                           f"Calculated fines for {len(overdue_transactions)} overdue books.\n"
                           f"Total fines: ${total_fines:.2f}")
        
        self.load_members()
        self.load_transactions()
    
    def generate_barcodes(self):
        """Generate barcodes for books (simulation)"""
        self.cursor.execute('SELECT id, isbn, title FROM books WHERE isbn IS NOT NULL AND isbn != ""')
        books_with_isbn = self.cursor.fetchall()
        
        barcode_window = tk.Toplevel(self.root)
        barcode_window.title("Barcode Generator")
        barcode_window.geometry("500x400")
        barcode_window.configure(bg='#ecf0f1')
        
        tk.Label(barcode_window, text="Generated Barcodes", font=('Arial', 16, 'bold'),
                bg='#ecf0f1').pack(pady=20)
        
        barcode_text = tk.Text(barcode_window, wrap=tk.WORD, height=20)
        barcode_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        barcode_content = "BARCODE GENERATION REPORT\n"
        barcode_content += "=" * 40 + "\n\n"
        
        for book in books_with_isbn[:20]:  # Limit to first 20 books
            barcode_content += f"Book ID: {book[0]}\n"
            barcode_content += f"ISBN: {book[1]}\n"
            barcode_content += f"Title: {book[2]}\n"
            barcode_content += f"Barcode: ||||| {book[1]} |||||\n"
            barcode_content += "-" * 30 + "\n\n"
        
        barcode_content += f"\nNote: Generated barcodes for {min(len(books_with_isbn), 20)} books.\n"
        barcode_content += "In a real system, these would be actual barcode images."
        
        barcode_text.insert('1.0', barcode_content)
        barcode_text.configure(state='disabled')
        
        messagebox.showinfo("Success", f"Generated barcodes for {len(books_with_isbn)} books!")
    
    def optimize_database(self):
        """Optimize database performance"""
        try:
            self.cursor.execute('VACUUM')
            self.cursor.execute('REINDEX')
            self.conn.commit()
            messagebox.showinfo("Success", "Database optimized successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Optimization failed: {str(e)}")
    
    def clear_old_records(self):
        """Clear old records from database"""
        clear_window = tk.Toplevel(self.root)
        clear_window.title("Clear Old Records")
        clear_window.geometry("300x200")
        clear_window.configure(bg='#ecf0f1')
        
        tk.Label(clear_window, text="Clear records older than:", font=('Arial', 12),
                bg='#ecf0f1').pack(pady=20)
        
        days_var = tk.StringVar(value="365")
        tk.Entry(clear_window, textvariable=days_var, width=10).pack()
        tk.Label(clear_window, text="days", bg='#ecf0f1').pack()
        
        def perform_clear():
            try:
                days = int(days_var.get())
                cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                
                # Clear old transactions
                self.cursor.execute('''
                    DELETE FROM transactions 
                    WHERE status = 'returned' AND return_date < ?
                ''', (cutoff_date,))
                
                cleared_count = self.cursor.rowcount
                self.conn.commit()
                
                messagebox.showinfo("Success", f"Cleared {cleared_count} old records!")
                clear_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear records: {str(e)}")
        
        tk.Button(clear_window, text="Clear Records", command=perform_clear,
                 bg='#e74c3c', fg='white', padx=20, pady=10).pack(pady=20)
    
    def save_settings(self):
        """Save system settings"""
        try:
            # In a real system, these would be saved to a config file or database
            settings = {
                'loan_period': self.loan_period_var.get(),
                'fine_per_day': self.fine_per_day_var.get(),
                'max_books': self.max_books_var.get()
            }
            
            with open('library_settings.json', 'w') as f:
                json.dump(settings, f)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def load_settings(self):
        """Load system settings"""
        try:
            if os.path.exists('library_settings.json'):
                with open('library_settings.json', 'r') as f:
                    settings = json.load(f)
                
                self.loan_period_var.set(settings.get('loan_period', '14'))
                self.fine_per_day_var.set(settings.get('fine_per_day', '0.50'))
                self.max_books_var.set(settings.get('max_books', '5'))
            
        except Exception as e:
            print(f"Failed to load settings: {e}")
    
    def update_status(self):
        """Update status bar with current information"""
        try:
            # Get current statistics
            self.cursor.execute('SELECT COUNT(*) FROM transactions WHERE status = "active"')
            active_loans = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM books WHERE available_copies = 0')
            unavailable_books = self.cursor.fetchone()[0]
            
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            status_text = (f"Welcome, {self.current_user[4]} | Role: {self.user_role} | "
                          f"Active Loans: {active_loans} | Unavailable Books: {unavailable_books} | "
                          f"Time: {current_time}")
            
            self.status_bar.configure(text=status_text)
            
            # Schedule next update
            self.root.after(30000, self.update_status)  # Update every 30 seconds
            
        except Exception as e:
            print(f"Status update error: {e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        Advanced Library Management System
        Version 2.0
        
        Features:
        ✓ User Authentication & Authorization
        ✓ Book Management (CRUD operations)
        ✓ Member Management
        ✓ Transaction Processing (Issue/Return/Renew)
        ✓ Book Reservations
        ✓ Fine Management
        ✓ Advanced Reporting
        ✓ Data Import/Export
        ✓ Database Backup/Restore
        ✓ Automated Notifications
        ✓ Barcode Generation
        ✓ Book Reviews & Ratings
        ✓ Statistical Dashboard
        ✓ Search & Filter
        ✓ Custom Report Builder
        ✓ Multi-user Support
        ✓ Inventory Management
        ✓ Financial Tracking
        ✓ System Settings
        
        Developed with Python, Tkinter, SQLite, and Matplotlib
        """
        
        messagebox.showinfo("About", about_text)
    
    def logout(self):
        """Logout current user"""
        if messagebox.askyesno("Confirm", "Are you sure you want to logout?"):
            self.current_user = None
            self.user_role = None
            self.main_frame.destroy()
            self.create_login_interface()
    
    def run(self):
        """Start the application"""
        try:
            self.load_settings()
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Application error: {str(e)}")
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.conn.close()
            self.root.destroy()

# Main execution
if __name__ == "__main__":
    try:
        # Create and run the application
        app = AdvancedLibraryManagementSystem()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()

"""
INSTALLATION INSTRUCTIONS:
1. Install required packages:
   pip install matplotlib numpy

2. Run the application:
   python library_management_system.py

3. Login credentials:
   Username: admin
   Password: admin123

FEATURES INCLUDED:
1. User Authentication & Role-Based Access
2. Advanced Book Management (Add/Edit/Delete/Search)
3. Member Management with History
4. Transaction Processing (Issue/Return/Renew/Reserve)
5. Automated Fine Calculation
6. Comprehensive Reporting System
7. Data Import/Export (CSV/JSON)
8. Database Backup & Restore
9. Notification System
10. Barcode Generation
11. Book Reviews & Ratings
12. Statistical Dashboard with Charts
13. Advanced Search & Filtering
14. Custom Report Builder
15. Inventory Management
16. Financial Tracking
17. System Settings Configuration
18. Database Optimization Tools
19. Multi-format Data Export
20. Animated GUI with Modern Design
21. Context Menus for Quick Actions
22. Real-time Status Updates
23. Overdue Book Management
24. Reservation System
25. Member Communication Tools

The system uses SQLite for data storage and includes full CRUD operations,
data validation, error handling, and a professional user interface.
"""