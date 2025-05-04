# DATX11-DIT561-VT25-93
### Group 93 - Emil Svensjö, Erik Gälldin, Linus Lindström, Maria Logren, Mikael Motin, Tabita Tengblad 
#### *Bachelor's thesis*
## Project Overview
Countless individuals rely on authentication systems to safeguard their personal and professional lives, from accessing secure accounts to protecting sensitive data. Yet, traditional password-based systems remain vulnerable to breaches, phishing attacks, and weak password practices, leaving users at risk.
Addressing this critical security challenge, this project is set on developing a user-friendly face and eye recognition authentication system. 

---

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

#### Face Anti-Spoofing Testing - *test_anti-spoofing.ipynb*

1. Download a suitable dataset. The [LCC Face Anti-Spoofing Dataset](https://www.kaggle.com/datasets/faber24/lcc-fasd) is readily available and has been used for testing in this project.

2. Place the dataset folder in the same directory as the testing notebook.

3. Ensure that spoofed images are stored in one folder and genuine (real) images in another. Then, set the following variables:
   - `DATASET_PATH_REAL` - path to the folder with genuine images
   - `DATASET_PATH_ATTACK` - path to the folder with spoofed images
   - `N_SPOOFED` - the number of spoofed images
   - `N_REAL` - the number of genuine images
   - `N_RUNS` - the desired number of test repetitions


