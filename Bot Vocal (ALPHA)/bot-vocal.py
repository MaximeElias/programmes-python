import tkinter as tk
import speech_recognition as sr
import pyttsx3
import requests
from datetime import datetime
import locale
import pygame
import os
import webbrowser
import json
import random

# Initialisation des modules
recognizer = sr.Recognizer()
engine = pyttsx3.init()
pygame.mixer.init()

# Définir la locale sur le français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

# Définir le dossier pour les musiques
music_directory = r"C:\Users\Maxime\Music"  # Chemin vers votre dossier de musique
tracks = [os.path.join(music_directory, f) for f in os.listdir(music_directory) if f.endswith('.mp3')]

# Variable de contrôle pour arrêter l'écoute
continue_listening = True

# Variable pour garder une trace de l'index de la musique en cours
current_track_index = 0

# Fichier pour sauvegarder les tâches
task_file = "tasks.json"

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=10)
        try:
            return recognizer.recognize_google(audio, language='fr-FR')
        except sr.UnknownValueError:
            return listen()
        except sr.RequestError:
            return "Erreur dans la reconnaissance vocale"

def get_weather(city):
    api_key = "03f749839352867c0a4e5e09c76d15ad"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return f"Je ne trouve pas la météo pour cette ville désolé."
    
    weather = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    return f"Il fait {temp} degrés avec {weather} à {city}."

def get_day_of_week():
    current_date = datetime.now()
    day = current_date.strftime("%A")  # Nom du jour
    date = current_date.strftime("%d %B %Y")  # Date complète (jour, mois, année)
    return f"Aujourd'hui, nous sommes {day}, {date}."

def get_current_time():
    current_time = datetime.now().strftime("%H:%M")
    return f"Il est actuellement {current_time}."

def search_internet(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Recherche pour {query}."

def get_news():
    api_key = "e3bac4bd47e94102afc2e5be29628305"
    url = f"https://newsapi.org/v2/top-headlines?country=fr&apiKey={api_key}&language=fr"
    response = requests.get(url)
    data = response.json()

    if data.get("status") != "ok":
        return "Erreur lors de la récupération des actualités."

    articles = data.get("articles", [])
    if not articles:
        return "Aucune actualité disponible pour le moment."

    news_summary = "Voici les dernières actualités :\n"
    for article in articles[:5]:
        title = article.get("title")
        url = article.get("url")
        news_summary += f"- {title} ({url})\n"

    return news_summary

def play_music(track):
    try:
        pygame.mixer.music.load(track)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()
        return f"Lecture de {os.path.basename(track)}"
    except Exception as e:
        return "Erreur lors de la lecture de la musique."

def play_next_music():
    global current_track_index

    if not tracks:
        return "Aucune musique disponible."

    current_track_index = (current_track_index + 1) % len(tracks)
    return play_music(tracks[current_track_index])

def pause_music():
    pygame.mixer.music.pause()
    return "Musique mise en pause."

def resume_music():
    pygame.mixer.music.unpause()
    return "Musique reprise."

def stop_music():
    pygame.mixer.music.stop()
    return "Musique arrêtée."

def save_tasks(tasks):
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

def load_tasks():
    if os.path.exists(task_file):
        with open(task_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def add_task(task):
    tasks.append(task)
    save_tasks(tasks)
    speak(f"Tâche ajoutée : {task}")

def remove_task(task):
    if task in tasks:
        tasks.remove(task)
        save_tasks(tasks)
        speak(f"Tâche supprimée : {task}")
    else:
        speak("Cette tâche n'existe pas.")

def show_tasks():
    if tasks:
        speak("Voici vos tâches :")
        for i, task in enumerate(tasks, 1):
            speak(f"Tâche {i}: {task}")
    else:
        speak("Vous n'avez aucune tâche pour le moment.")

tasks = load_tasks()

def start_listening():
    global continue_listening
    if not continue_listening:
        return

    activation_phrase = "alpha"
    command = listen()

    if activation_phrase in command.lower():
        speak("Je vous écoute.")
        
        while continue_listening:
            command = listen()
            result_label.config(text=f"Vous avez dit : {command}")
            
            if "bonjour" in command.lower() or "bonsoir" in command.lower() or "salut" in command.lower():
                speak("Bonjour, comment puis-je vous aider ?")
 
            if "ça va" in command.lower() or "tu vas bien" in command.lower() or "comment vas tu" in command.lower():
                speak("Je vais bien et vous ?")
            
            if "merci" in command.lower():
                speak("Avec plaisir !")
                
            elif "info" in command.lower() or "informations" in command.lower():
                day_report = get_day_of_week()
                speak(day_report)
                result_label.config(text=day_report)
                weather_report = get_weather("douai")
                speak(weather_report)
                time_report = get_current_time()
                speak(time_report)
                result_label.config(text=time_report)
                
            elif "météo" in command.lower() or "quel temps" in command.lower():
                speak("Pour quelle ville souhaitez-vous la météo ?")
                city = listen()
                weather_report = get_weather(city)
                speak(weather_report)
            
            elif "jour" in command.lower() or "date" in command.lower():
                day_report = get_day_of_week()
                speak(day_report)
                result_label.config(text=day_report)
            
            elif "heure" in command.lower():
                time_report = get_current_time()
                speak(time_report)
                result_label.config(text=time_report)
            
            elif "actualité" in command.lower():
                news_report = get_news()
                speak(news_report)
                result_label.config(text=news_report)
                
            elif "recherche" in command.lower():
                speak("Que voulez-vous rechercher ?")
                query = listen()
                speak(search_internet(query))
                
            elif "musique" in command.lower():
                if tracks:
                    random_track = random.choice(tracks)
                    speak(play_music(random_track))
                else:
                    speak("Aucune musique trouvée.")
            
            elif "suivante" in command.lower():
                speak(play_next_music())

            elif "pause" in command.lower():
                speak(pause_music())

            elif "reprendre" in command.lower():
                speak(resume_music())

            elif "arrêter" in command.lower() or "stop" in command.lower():
                speak(stop_music())
                
            elif "ajouter tâche" in command.lower():
                speak("Quelle tâche voulez-vous ajouter ?")
                task = listen()
                add_task(task)

            elif "supprimer tâche" in command.lower():
                speak("Quelle tâche voulez-vous supprimer ?")
                task = listen()
                remove_task(task)

            elif "voir tâche" in command.lower():
                show_tasks()
                
            elif "bonne nuit" in command.lower() or "au revoir" in command.lower() or "arrêt" in command.lower():
                speak("Au revoir et à bientôt")
                result_label.config(text="Fermeture de l'assistant")
                continue_listening = False
                root.quit()
                
            else:
                speak("Je ne comprends pas encore cette commande.")
    
    if continue_listening:
        start_listening()

# Création de la fenêtre avec Tkinter
root = tk.Tk()
root.title("Assistant Vocal")

# Créer un cadre pour contenir le contenu
frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20)
frame.pack(pady=20)

# Créer un label pour les résultats
result_label = tk.Label(frame, text="Alpha assistante vocale", font=("Arial", 14), bg="#ffffff")
result_label.pack(pady=20)

# Saluer l'utilisateur au démarrage
speak("Bonjour, je m'appelle Alpha je suis à votre écoute")
start_listening()

# Lancer l'application Tkinter
root.mainloop()