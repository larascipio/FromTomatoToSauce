import sqlite3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
key = os.getenv("MISTRAL_API_KEY")

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()

# Create the table
cursor.execute('''
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL
)
''')
conn.commit()

# Function to add a recipe
def add_recipe():
    name = input("🍽️ Enter recipe name: ")
    ingredients = input("🧂 Enter ingredients (comma-separated): ")
    instructions = input("📋 Enter cooking instructions: ")

    cursor.execute('''
    INSERT INTO recipes (name, ingredients, instructions)
    VALUES (?, ?, ?)
    ''', (name, ingredients, instructions))
    conn.commit()
    print(f"✅ Recipe '{name}' added successfully!\n")

# Function to search recipes by ingredient
def search_by_ingredient():
    ingredient = input("🔍 Enter an ingredient to search for: ").lower()
    cursor.execute('SELECT name, ingredients FROM recipes')
    results = cursor.fetchall()

    print(f"\n📚 Recipes containing '{ingredient}':")
    found = False
    for name, ingredients in results:
        if ingredient in ingredients.lower():
            print(f"- {name}")
            found = True
    if not found:
        print("No recipes found with that ingredient.\n")

def get_all_recipes():
    cursor.execute('SELECT name, ingredients, instructions FROM recipes')
    return cursor.fetchall()   

# Main loop
def main():
    print("👩‍🍳 Welcome to Your Recipe Agent!")
    while True:
        print("\nChoose an option:")
        print("1. Add a new recipe")
        print("2. Search recipes by ingredient")
        print("3. Get a list of recipes")        
        print("4. Exit")

        choice = input("Enter your choice (1/2/3): ")
        if choice == '1':
            add_recipe()
        elif choice == '2':
            search_by_ingredient()
        elif choice == '3':
            recipes = get_all_recipes()
            print("\n📚 All Recipes:")
            for name, ingredients, instructions in recipes:
                print(f"\n🍲 {name}\n🧂 Ingredients: {ingredients}\n📋 Instructions: {instructions}\n")
            break
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

    conn.close()

main()

