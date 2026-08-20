from backend.db.database import Base, engine
from backend.db import models                                                

def main():
    print("Creating application tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    main()
