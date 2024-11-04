import tkinter as tk
from tkinter import messagebox, font
import json

RECIPES_FILE = 'Bot Cuisine (SOMA)\\recipes.json'

def load_recipes():
    try:
        with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        messagebox.showinfo("Erreur", "Le fichier recipes.json n'a pas été trouvé.")
        return {}
    except json.JSONDecodeError:
        messagebox.showinfo("Erreur", "Le fichier recipes.json n'est pas correctement formaté.")
        return {}

def search_recipes():
    ingredients = entry_ingredients.get().lower().split(',')
    ingredients = [ingredient.strip() for ingredient in ingredients]

    recipes = load_recipes()
    
    if not recipes:
        messagebox.showinfo("Erreur", "Aucune recette chargée. Vérifiez le fichier recipes.json.")
        return

    results = []
    for name, details in recipes.items():
        recipe_ingredients = [ingredient.lower() for ingredient in details['ingredients']]
        if any(ingredient in recipe_ingredients for ingredient in ingredients):
            results.append(name)

    display_results(results)

def display_results(results):
    for widget in frame_results.winfo_children():
        widget.destroy()
    
    if results:
        for recipe in results:
            show_recipe_summary(recipe)
    else:
        label_no_results = tk.Label(frame_results, text="Aucune recette trouvée.", font=("Helvetica", 12))
        label_no_results.pack(pady=10)

def show_recipe_summary(recipe_name):
    recipes = load_recipes()
    recipe = recipes.get(recipe_name)
    
    if recipe:
        recipe_frame = tk.Frame(frame_results, bg="#ffffff", bd=2, relief="groove", padx=10, pady=10)
        recipe_frame.pack(pady=5, fill='x')
        
        recipe_label = tk.Label(recipe_frame, text=f"Recette: {recipe_name}", font=("Helvetica", 14, "bold"), bg="#ffffff")
        recipe_label.pack()
        
        ingredients = ", ".join(recipe['ingredients'])
        ingredients_label = tk.Label(recipe_frame, text=f"Ingrédients: {ingredients}", bg="#ffffff")
        ingredients_label.pack()

        # Bouton pour afficher les détails
        details_button = tk.Button(recipe_frame, text="Voir détails", command=lambda: show_recipe_details(recipe_name), bg="#4CAF50", fg="white")
        details_button.pack(pady=5)

def show_recipe_details(recipe_name):
    recipes = load_recipes()
    recipe = recipes.get(recipe_name)
    
    if recipe:
        # Nouvelle fenêtre pour les détails
        details_window = tk.Toplevel(root)
        details_window.title(f"Détails de la recette - {recipe_name}")
        details_window.geometry("450x500")
        details_window.configure(bg="#f9f9f9")
        
        # Affichage du titre de la recette
        title_label = tk.Label(details_window, text=recipe_name, font=("Helvetica", 18, "bold", "underline"), bg="#4CAF50", fg="white", pady=10)
        title_label.pack(fill="x")
        
        # Temps de préparation
        prep_time = recipe.get("prep_time", "Non spécifié")
        prep_time_frame = tk.Frame(details_window, bg="#f0f0f0", bd=1, relief="solid")
        prep_time_frame.pack(pady=10, padx=10, fill="x")
        
        prep_time_label = tk.Label(prep_time_frame, text=f"Temps de préparation : {prep_time}", font=("Helvetica", 12), bg="#f0f0f0", anchor="w")
        prep_time_label.pack(padx=10, pady=5, fill="x")
        
        # Ingrédients
        ingredients_frame = tk.Frame(details_window, bg="#ffffff", bd=1, relief="solid")
        ingredients_frame.pack(pady=10, padx=10, fill="x")
        
        ingredients_title = tk.Label(ingredients_frame, text="Ingrédients", font=("Helvetica", 14, "bold", "underline"), bg="#ffffff", fg="#4CAF50", anchor="w")
        ingredients_title.pack(padx=10, pady=5)
        
        ingredients = "\n".join([f"- {ingredient}" for ingredient in recipe['ingredients']])
        ingredients_label = tk.Label(ingredients_frame, text=ingredients, font=("Helvetica", 12), bg="#ffffff", anchor="w", justify="left", padx=10)
        ingredients_label.pack(fill="x", padx=10, pady=5)
        
        # Préparation
        preparation_frame = tk.Frame(details_window, bg="#ffffff", bd=1, relief="solid")
        preparation_frame.pack(pady=10, padx=10, fill="x")
        
        preparation_title = tk.Label(preparation_frame, text="Préparation", font=("Helvetica", 14, "bold", "underline"), bg="#ffffff", fg="#4CAF50", anchor="w")
        preparation_title.pack(padx=10, pady=5)
        
        preparation_steps = "\n".join(recipe.get("preparation_steps", ["Pas de préparation détaillée disponible"]))
        preparation_label = tk.Label(preparation_frame, text=preparation_steps, font=("Helvetica", 12), bg="#ffffff", anchor="w", justify="left", wraplength=400, padx=10)
        preparation_label.pack(fill="x", padx=10, pady=5)
    else:
        messagebox.showinfo("Erreur", "Recette non trouvée.")

# Création de la fenêtre principale
root = tk.Tk()
root.title("Assistant de Cuisine")
root.configure(bg="#e8f0f2")

custom_font = font.Font(family="Helvetica", size=12)

main_frame = tk.Frame(root, bg="#e8f0f2", padx=20, pady=20)
main_frame.pack(padx=10, pady=10)

welcome_label = tk.Label(main_frame, text="Bienvenue dans l'Assistant de Cuisine !", bg="#e8f0f2", font=("Helvetica", 16, "bold"))
welcome_label.pack(pady=10)

frame_ingredients = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove", padx=10, pady=10)
frame_ingredients.pack(pady=10)

label_ingredients = tk.Label(frame_ingredients, text="Ingrédients (séparés par des virgules) :", bg="#ffffff", font=custom_font)
label_ingredients.pack()

entry_ingredients = tk.Entry(frame_ingredients, width=50, font=custom_font, bd=2, relief="solid")
entry_ingredients.pack(pady=10)

button_search = tk.Button(frame_ingredients, text="Rechercher des recettes", command=search_recipes, font=custom_font, bg="#4CAF50", fg="white", padx=10)
button_search.pack(pady=10)

frame_results = tk.Frame(main_frame, bg="#e8f0f2")
frame_results.pack(pady=10)

root.mainloop()