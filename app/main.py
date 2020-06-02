from app import create_app
import sys

PORT = "5000"

def main(args=[]):
    app_port = PORT if len(args) <=1 else args[1]

    app = create_app()
    
    print("Raising AppServer in port", app_port)
    app.run(host="0.0.0.0", port=app_port)

# -- Run

if __name__ == '__main__':
    main(sys.argv)