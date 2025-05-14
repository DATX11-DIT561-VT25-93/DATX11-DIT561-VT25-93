import os
import subprocess
import sys

# Specify the virtual environment name
venv_name = ".venv" 

# Detect the operating system
is_windows = os.name == "nt"

# Set paths for the virtual environment and Python executable
venv_path = os.path.join(os.getcwd(), venv_name)
python_executable = (
    os.path.join(venv_path, "Scripts", "python.exe") if is_windows else os.path.join(venv_path, "bin", "python")
)
gitignore_path = os.path.join(os.getcwd(), ".gitignore")

# Create the virtual environment if it doesn't exist
if not os.path.exists(venv_path):
    print(f"Creating virtual environment '{venv_name}'...")
    subprocess.check_call([sys.executable, "-m", "venv", venv_path])
else:
    print(f"Virtual environment '{venv_name}' already exists.")

# Install required libraries
print("Installing required libraries in the virtual environment...")
try:
    subprocess.run(
        [python_executable, "-m", "pip", "install", "jupyter", "ipykernel", "opencv-python", "numpy", "matplotlib", "pillow", "pandas", "scikit-learn", "tensorflow==2.15.0", "torch", "keras==2.15.0", "ml-dtypes==0.2.0", "tensorboard==2.15.0", "deepface==0.0.79", "Flask", "Flask-SQLAlchemy", "supabase", "python-dotenv", "onnxruntime", "cryptography"],
        check=True,
    )
    print("Libraries installed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error installing libraries: {e}")
    sys.exit(1)

# Register the virtual environment as a Jupyter kernel
print("Registering the virtual environment as a Jupyter kernel...")
try:
    subprocess.run(
        [python_executable, "-m", "ipykernel", "install", "--user", "--name", venv_name, "--display-name", f"Python ({venv_name})"],
        check=True,
    )
    print(f"Kernel 'Python ({venv_name})' is now available in Jupyter.")
    print("Select the kernel to use the virtual environment in Jupyter notebooks.")
except subprocess.CalledProcessError as e:
    print(f"Error registering the kernel: {e}")
    sys.exit(1)
