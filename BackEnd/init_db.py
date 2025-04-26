import database as db
import os

def main():
    # Check if database exists
    if os.path.exists(db.DB_PATH):
        user_input = input(f"Database already exists at {db.DB_PATH}. Reset it? (y/n): ")
        if user_input.lower() == 'y':
            try:
                os.remove(db.DB_PATH)
                print(f"Deleted existing database.")
            except Exception as e:
                print(f"Error deleting database: {str(e)}")
                return
        else:
            print("Database initialization canceled.")
            return
    
    # Initialize the database
    try:
        db.init_db()
        print(f"Database initialized successfully at {db.DB_PATH}")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

if __name__ == "__main__":
    main()
