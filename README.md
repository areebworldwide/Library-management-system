# Advanced Library Management System

A comprehensive library management application built with Python, Tkinter, SQLite, and Matplotlib. This system provides complete library operations management with a modern, animated graphical user interface.

## Features

### Core Functionality
- **User Authentication & Authorization** - Role-based access control (Admin/Member)
- **Book Management** - Add, edit, delete, search books with detailed information
- **Member Management** - Complete member registration and profile management
- **Transaction Processing** - Issue, return, renew, and reserve books
- **Fine Management** - Automated fine calculation and tracking
- **Reservation System** - Book reservation and waitlist management

### Advanced Features
- **Statistical Dashboard** - Interactive charts and real-time statistics
- **Comprehensive Reporting** - Multiple report types with custom report builder
- **Data Import/Export** - CSV and JSON support for books and member data
- **Database Management** - Backup, restore, and optimization tools
- **Notification System** - Automated overdue and due-soon notifications
- **Review System** - Book ratings and reviews by members
- **Barcode Generation** - ISBN barcode simulation for books
- **Search & Filter** - Advanced search capabilities across all data
- **Inventory Tracking** - Real-time availability and location management

### Technical Features
- **Animated GUI** - Modern interface with color animations and smooth transitions
- **Context Menus** - Right-click menus for quick actions
- **Real-time Updates** - Live status updates and data synchronization
- **Multi-format Export** - Support for CSV, JSON, and SQL formats
- **System Settings** - Configurable loan periods, fines, and limits

## Installation

### Prerequisites
- Python 3.7 or higher
- Required Python packages (install using pip)

### Install Dependencies
```bash
pip install matplotlib numpy
```

### Download and Run
1. Save the Python script as `library_management_system.py`
2. Run the application:
```bash
python library_management_system.py
```

## Default Login Credentials

**Administrator Account:**
- Username: `admin`
- Password: `admin123`

## Database Structure

The system uses SQLite database (`library_system.db`) with the following tables:

### Users Table
- User authentication and profile information
- Role-based access control (admin/member)
- Fine balance tracking
- Membership status management

### Books Table
- Complete book catalog with ISBN, title, author
- Category classification and publisher information
- Inventory tracking (total/available copies)
- Location and pricing information

### Transactions Table
- Issue/return/renewal records
- Due date tracking and fine calculation
- Transaction history and status

### Reservations Table
- Book reservation queue
- Priority-based reservation system

### Reviews Table
- Book ratings (1-5 stars)
- Member reviews and feedback

## User Guide

### For Administrators

#### Dashboard
- View system statistics and charts
- Monitor active loans and overdue books
- Track member activity and popular books

#### Book Management
- Add new books with complete details
- Edit existing book information
- Delete books (with safety checks)
- Import books from CSV files
- Generate barcodes for inventory

#### Member Management
- View all registered members
- Edit member profiles and status
- Suspend/activate memberships
- Send messages to members
- View member transaction history

#### Transaction Management
- Issue books to members
- Process book returns
- Renew existing loans
- Manage book reservations
- Calculate and apply fines

#### Reporting
- Generate overdue books reports
- Create popular books analysis
- Member activity summaries
- Financial reports with fine tracking
- Inventory status reports
- Custom report builder

#### System Management
- Configure system settings (loan periods, fines)
- Backup and restore database
- Import/export data
- Send automated notifications
- Optimize database performance

### For Members

#### Book Search
- Search by title, author, ISBN, or category
- View book details and availability
- Read reviews and ratings
- Reserve unavailable books

#### Account Management
- View transaction history
- Check current loans and due dates
- View fine balance
- Add book reviews and ratings

## System Configuration

### Settings (Admin Only)
- **Default Loan Period**: 14 days (configurable)
- **Fine Per Day**: $0.50 (configurable)
- **Maximum Books Per Member**: 5 (configurable)
- **Membership Status**: Active, Suspended, Inactive

### File Locations
- Database: `library_system.db`
- Settings: `library_settings.json`
- Exports: User-specified locations

## Data Import Format

### CSV Book Import Format
Required columns:
- ISBN
- Title
- Author
- Category
- Publisher
- Year
- Copies
- Location
- Price
- Description

## Backup and Recovery

### Automatic Backups
- Database can be backed up to `.db` or `.sql` formats
- Backup includes all tables and data
- Restore functionality with confirmation prompts

### Data Export Options
- **Books**: Complete catalog export
- **Members**: Member database export
- **Transactions**: Full transaction history
- **All Data**: Complete system export

## Security Features

- Password hashing (SHA-256)
- Role-based access control
- Transaction logging
- Data validation and sanitization
- Secure database connections

## Error Handling

- Comprehensive exception handling
- User-friendly error messages
- Data validation before database operations
- Rollback capabilities for failed transactions

## Performance Optimization

- Database indexing for fast searches
- Efficient query optimization
- Memory management for large datasets
- Background processing for reports

## Troubleshooting

### Common Issues

**Database Connection Errors:**
- Ensure write permissions in application directory
- Check if database file is locked by another process

**Import Failures:**
- Verify CSV format matches required structure
- Check for special characters in data

**Display Issues:**
- Ensure all required packages are installed
- Check screen resolution compatibility

### Support

For technical support or feature requests:
1. Check the error messages for specific details
2. Verify all dependencies are installed
3. Ensure database permissions are correct
4. Review the installation steps

## System Requirements

### Minimum Requirements
- Operating System: Windows 7+, macOS 10.12+, Linux (Ubuntu 16.04+)
- Python: 3.7+
- RAM: 2GB minimum
- Storage: 100MB for application + data storage
- Display: 1024x768 minimum resolution

### Recommended Requirements
- Python: 3.9+
- RAM: 4GB or higher
- Storage: 1GB+ for large libraries
- Display: 1366x768 or higher

## License

This is a demonstration project for educational purposes. The code includes comprehensive comments and documentation for learning purposes.

## Version History

### Version 2.0 (Current)
- Complete rewrite with advanced features
- Modern animated GUI
- Comprehensive reporting system
- Data import/export capabilities
- Advanced search and filtering
- Review and rating system
- Statistical dashboard with charts

### Version 1.0
- Basic library management features
- Simple user interface
- Core CRUD operations

## Contributing

This is an educational project demonstrating library management system concepts. The code is fully documented with comments explaining each function and feature.

## Acknowledgments

Built using:
- **Python** - Core programming language
- **Tkinter** - GUI framework
- **SQLite** - Database management
- **Matplotlib** - Data visualization
- **NumPy** - Numerical computations
