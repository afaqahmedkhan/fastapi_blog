from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

posts = [
    {
        "id": 1,
        "author": "DadJokeMaster",
        "title": "Why don’t skeletons fight each other?",
        "content": "They don’t have the guts!",
        "date_posted": "2026-09-17"
    },
    {
        "id": 2,
        "author": "PunnyParent",
        "title": "What do you call a fake noodle?",
        "content": "An impasta!",
        "date_posted": "2026-09-16"
    },
    {
        "id": 3,
        "author": "JokeGenius",
        "title": "Why did the scarecrow win an award?",
        "content": "Because he was outstanding in his field!",
        "date_posted": "2026-09-15"
    },
    {
        "id": 4,
        "author": "LaughingDad",
        "title": "What’s brown and sticky?",
        "content": "A stick!",
        "date_posted": "2026-09-14"
    },
    {
        "id": 5,
        "author": "ChuckleChampion",
        "title": "How do you organize a space party?",
        "content": "You planet!",
        "date_posted": "2026-09-13"
    },
    {
        "id": 6,
        "author": "DadJokeKing",
        "title": "Why can’t you trust an atom?",
        "content": "Because they make up everything!",
        "date_posted": "2026-09-12"
    },
    {
        "id": 7,
        "author": "GiggleGuru",
        "title": "What’s the best time to go to the dentist?",
        "content": "Tooth-hurty! (2:30)",
        "date_posted": "2026-09-11"
    },
    {
        "id": 8,
        "author": "ComedyDad",
        "title": "Why did the bicycle fall over?",
        "content": "Because it was two-tired!",
        "date_posted": "2026-09-10"
    },
    {
        "id": 9,
        "author": "JesterDad",
        "title": "What do you call cheese that isn’t yours?",
        "content": "Nacho cheese!",
        "date_posted": "2026-09-09"
    },
    {
        "id": 10,
        "author": "FunnyFather",
        "title": "Why did the math book look sad?",
        "content": "Because it had too many problems!",
        "date_posted": "2026-09-08"
    }
]

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/post", response_class=HTMLResponse, include_in_schema=False)
def home():
  return f"<h1>{posts[0]['title']}</h1>"

@app.get("/api/v1/posts")
def get_posts():
  return posts

