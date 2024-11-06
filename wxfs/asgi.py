from wxfs import create_app

print("#### asgi")
connexion_app, flask_app, app_db = create_app()
