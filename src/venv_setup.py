import os
import subprocess
import sys

# Specify the virtual environment name
venv_name = ".venv"  # Change this to your desired name

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

# Add virtual environment to .gitignore
if os.path.exists(gitignore_path):
    with open(gitignore_path, "r") as gitignore_file:
        gitignore_content = gitignore_file.readlines()

    if venv_name + "/" not in [line.strip() for line in gitignore_content]:
        with open(gitignore_path, "a") as gitignore_file:
            gitignore_file.write(f"\n{venv_name}/\n")
        print(f"Added '{venv_name}/' to .gitignore.")
    else:
        print(f"'{venv_name}/' is already in .gitignore.")
else:
    with open(gitignore_path, "w") as gitignore_file:
        gitignore_file.write(f"{venv_name}/\n")
    print(f".gitignore created and added '{venv_name}/'.")

# Install required libraries
print("Installing required libraries in the virtual environment...")
try:
    subprocess.run(
        [python_executable, "-m", "pip", "install", "jupyter", "ipykernel", "opencv-python", "numpy", "matplotlib", "pillow", "pandas", "albumentations", "scikit-learn", "tensorflow", "torch", "tf-keras", "deepface", "Flask", "Flask-SQLAlchemy", "supabase", "python-dotenv", "onnxruntime"],
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
