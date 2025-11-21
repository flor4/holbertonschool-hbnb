# 🏠 HBnB - Business Logic Layer (Part 2)

## 📘 Overview
This project is part of the **Holberton School HBnB Clone**.  
It focuses on implementing the **core business logic classes** (`User`, `Place`, `Review`, and `Amenity`) and their relationships, based on the UML design from Part 1.

---

## 🗂️ Project Structure
part2/

holbertonschool-hbnb/

│
├── api/

└── v1/

└── init.py

├── models/

│ │ ├── init.py

│    │   ├── BaseModel.py ***Defines BaseModel class (UUID, timestamps, save, update)***

│ │ ├── user.py ***Defines User entity (inherits from BaseModel)***

│ │ ├── place.py ***Defines Place entity (inherits from BaseModel)***

│ │ ├── review.py ***Defines Review entity (inherits from BaseModel)***

│   │ └── amenity.py ***Defines Amenity entity (inherits from BaseModel)***


├── persistence/

│ │  ├── init.py

│ │  └── repository.py ## Handles data storage (in-memory or database)


├── services/

│ │├── init.py

│ │ └── facade.py ***Business operations that coordinate multiple models***


├── config.py ***Application configuration (environment setup, etc.)***

├── run.py ***Entry point for running the project***

├── requirements.txt ***Python dependencies list***

└── README.md ***Project documentation (this file)***


## ⚙️ Setup and Run

### 1️⃣ Install dependencies
pip install -r requirements.txt


### 2️⃣ Run the application

python3 run.py

### 🧩 Key Concepts
BaseModel: Provides id, created_at, updated_at, and CRUD methods.

User: Represents a system user.

Place: Represents a property listed by a user.

Review: Represents feedback for a place.

Amenity: Represents features or services available in a place.

### 🔗 Relationships
User → Place: one-to-many (a user owns several places).

Place → Review: one-to-many (a place has many reviews).

Place ↔ Amenity: many-to-many (a place can have several amenities).
