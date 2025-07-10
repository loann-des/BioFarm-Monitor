from web_app.views import app
print(">>> Fichier app.py exécuté depuis :", __file__)

if __name__ == '__main__':
    print(">>> FLASK_APP lancé depuis :", __file__)
    app.run(host='0.0.0.0', port=8000, debug=True)