from app import app

# Vercel serverless function ke liye
def handler(environ, start_response):
    return app(environ, start_response)

# Agar aapko WSGI server ke saath use karna ho
if __name__ == "__main__":
    app.run()