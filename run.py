from dotenv import load_dotenv
from app import create_app

# umgebungsvariablen aus der .env Datei laden
load_dotenv()


app = create_app()

if __name__ == '__main__':
    # port 5000 
    app.run(debug=True, port=5000)