# DATX11-DIT561-VT25-93
### Group 93 - Emil Svensjö, Erik Gälldin, Linus Lindström, Maria Logren, Mikael Motin, Tabita Tengblad 
#### *Bachelor's thesis*
## Project Overview
Countless individuals rely on authentication systems to safeguard their personal and professional lives, from accessing secure accounts to protecting sensitive data. Yet, traditional password-based systems remain vulnerable to breaches, phishing attacks, and weak password practices, leaving users at risk.
Addressing this critical security challenge, this project is set on developing a user-friendly face recognition authentication system. 


## Running the Web Application
This section outlines the essential steps to get the web application up and running, including setting up a Python virtual environment, installing prerequisites, configuring the .env file, and completing the initial setup.

If you’ve already completed all the steps below (including the first-time setup) you can start the application by running the following command from within the `flaskr/` directory:
```
npm run start
```
### Before You Begin

It is recommended to use a Python Virtual Environment (`.venv`) for package management.

- If you are unfamiliar with virtual environments, you can create one by running:
  ```
  python venv_setup.py
  ```
- If you are familiar with virtual environments, use the following to install dependencies:
  ```
  pip install -r src/requirements.txt
  ```

### Prerequisites

- Python (recommended version: `3.10`)
- Node.js and npm (Node Package Manager)

### Configuring the `.env` File

Create a `.env` file inside the `/flaskr` directory (`/flaskr/.env`) with the following structure:

```
SUPABASE_URL=XXXXXXXXXXXXX
SUPABASE_KEY=XXXXXXXXXXXXX
SUPABASE_DATABASE_PASSWORD=XXXXXXXXXXXXX
AESGCM_SECRET_KEY=XXXXXXXXXXXXX
SENDER_PASSWORD=XXXXXXXXXXXXX
SENDER_EMAIL=XXXXXXXXXXXXX
```

> **Note for supervisors/examiners**: Please contact us to receive the required credentials.

Replace each `XXXXXXXXXXXXX` with the appropriate URL, key, email, or password.

---

### First-Time Setup

1. Open a terminal and navigate to the `/flaskr` folder:
   ```
   cd flaskr
   ```
2. Install the required Node.js packages:
   ```
   npm install
   ```
3. Start the application:
   ```
   npm run start
   ```

Once the server is running, open the link displayed in the terminal, typically:
```
http://127.0.0.1:5000/
```

> Note: The application may take a few seconds to initialize. Console messages will appear before the URL is available.

---

### Common Issues

- **TensorFlow compatibility**: If using a Python version newer than `3.10`, you may encounter issues with TensorFlow. Downgrading to Python `3.10` is recommended. In some cases, manually installing `tensorflow==2.15.0` may resolve the issue.
  
- **Flask not recognized**: If you receive an error like `Flask is not recognized as an internal or external command`, ensure that your IDE is using the correct `.venv` interpreter. Try restarting your IDE after selecting the virtual environment.

## Running the Test Notebooks

Before running the general performance tests and the anti-spoofing tests, you must download the required datasets and, in some cases, organize them in a specific directory structure. Below are the steps for setting up and running each notebook.

#### General Performance Testing - *performance_test_recognition.ipynb*

1. Download the dataset you wish to test. Recommended, readily available options, also used in the project report, include:
   - [FEI Face Database](https://fei.edu.br/~cet/facedatabase.html)
   - [Georgia Tech Face Database](https://www.anefian.com/research/face_reco.htm)
   - [LFW Dataset](https://www.kaggle.com/datasets/jessicali9530/lfw-dataset)

2. Place the dataset folder in the same directory as the testing notebook.

3. Ensure the dataset folder contains one subfolder per individual (i.e., one folder for each person’s images), as expected by the face detection and feature extraction script.

4. Set the following variables in the notebook:
   - `DATASET_PATH` - path to the dataset folder
   - `REF_IMG_INDEX` - **11** for the FEI dataset and **0** for the Georgia Tech and LFW datasets

5. Run the notebook.

#### Face Anti-Spoofing Testing - *test_anti-spoofing.ipynb*

1. Download a suitable dataset. The [LCC Face Anti-Spoofing Dataset](https://www.kaggle.com/datasets/faber24/lcc-fasd) is readily available and has been used for testing in this project.

2. Place the dataset folder in the same directory as the testing notebook.

3. Ensure that spoofed images are stored in one folder and genuine (real) images in another. Then, set the following variables:
   - `DATASET_PATH_REAL` - path to the folder with genuine images
   - `DATASET_PATH_ATTACK` - path to the folder with spoofed images
   - `N_SPOOFED` - the number of spoofed images
   - `N_REAL` - the number of genuine images
   - `N_RUNS` - the desired number of test repetitions

4. Run the notebook.


