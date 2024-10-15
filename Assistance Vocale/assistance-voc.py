import tkinter as tk
import speech_recognition as sr
import pyttsx3
import requests
from datetime import datetime
import locale
import pygame
import os
import webbrowser

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

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=5)
        try:
            return recognizer.recognize_google(audio, language='fr-FR')
        except sr.UnknownValueError:
            speak("Je n'ai pas compris. Pouvez-vous répéter ?")
            return listen()
        except sr.RequestError:
            return "Erreur dans la reconnaissance vocale"

def get_weather(city):
    api_key = "03f749839352867c0a4e5e09c76d15ad"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return f"Je ne trouve pas la météo pour ville."
    
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
        pygame.mixer.music.play()
        return f"Lecture de {os.path.basename(track)}."
    except Exception as e:
        return "Erreur lors de la lecture de la musique."

def pause_music():
    pygame.mixer.music.pause()
    return "Musique mise en pause."

def resume_music():
    pygame.mixer.music.unpause()
    return "Musique reprise."

def stop_music():
    pygame.mixer.music.stop()
    return "Musique arrêtée."

def start_listening():
    global continue_listening
    if not continue_listening:
        return

    command = listen()
    result_label.config(text=f"Vous avez dit : {command}")
    
    if "bonjour" in command.lower():
        speak("Bonjour Maxime, comment puis-je vous aider ?")
        
    elif "météo" in command.lower():
        speak("Pour quelle ville souhaitez-vous la météo ?")
        city = listen()
        weather_report = get_weather(city)
        speak(weather_report)
    
    elif "jour" in command.lower():
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
            speak(play_music(tracks[0]))
        else:
            speak("Aucune musique trouvée.")

    elif "pause" in command.lower():
        speak(pause_music())

    elif "reprendre" in command.lower():
        speak(resume_music())

    elif "arrêter" in command.lower():
        speak(stop_music())
        
    elif "bonne nuit" in command.lower():
        speak("Au revoir Maxime !")
        result_label.config(text="Fermeture de l'assistant")
        continue_listening = False
        root.quit()
        
    else:
        speak("Je ne comprends pas encore cette commande.")
    
    if continue_listening:
        start_listening()

# Fonction pour lancer l'assistant vocal
def launch_assistant():
    result_label.config(text="Assistant en cours d'exécution...")
    start_listening()

# Fonction pour arrêter l'assistant vocal
def stop_assistant():
    global continue_listening
    continue_listening = False
    result_label.config(text="Assistant arrêté.")

# Création de la fenêtre avec Tkinter
root = tk.Tk()
root.title("Assistant Vocal")

# Créer un cadre pour contenir le contenu
frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20)
frame.pack(pady=20)

# Créer un label pour les résultats
result_label = tk.Label(frame, text="Cliquez sur 'Démarrer' pour lancer l'assistant", font=("Arial", 14), bg="#ffffff")
result_label.pack(pady=20)

# Créer un bouton pour démarrer l'assistant
start_button = tk.Button(frame, text="Démarrer", font=("Arial", 12), command=launch_assistant)
start_button.pack(pady=10)

# Créer un bouton pour arrêter l'assistant
stop_button = tk.Button(frame, text="Arrêter", font=("Arial", 12), command=stop_assistant)
stop_button.pack(pady=10)

# Saluer l'utilisateur au démarrage
speak("Bonjour Maxime, bienvenue dans votre assistant vocal !")

# Lancer l'application Tkinter
root.mainloop()