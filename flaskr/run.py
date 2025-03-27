import subprocess
from app import create_app

app = create_app()

def run_tailwind():
    """Runs the Tailwind CSS compiler"""
    subprocess.Popen(['npx', 'tailwindcss', '-i', './app/static/css/input.css', '-o', './app/static/css/output.css', '--watch'])

if __name__ == '__main__':
    run_tailwind()  # Start Tailwind CSS compiler
    app.run(debug=True)
