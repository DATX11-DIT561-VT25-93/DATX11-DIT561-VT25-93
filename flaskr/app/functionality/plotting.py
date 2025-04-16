import matplotlib.pyplot as plt
import matplotlib as mpl

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Global font
mpl.rcParams['font.family'] = 'Times New Roman'

# Global font size
mpl.rcParams['font.size'] = 18

def plot_conf_mat(y_true, y_pred):
    conf_mat = confusion_matrix(y_true, y_pred)

    # Plotting the confusion matrix
    conf_mat_display = ConfusionMatrixDisplay(conf_mat)
    conf_mat_display.plot()
    
    # Labels
    plt.xlabel("Predicted Value")
    plt.ylabel("True Value")

    plt.show()

def get_tpr_and_fpr(y_true, y_pred):
    conf_mat = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = conf_mat.ravel()

    tpr = tp / (tp + fn)  # True positive rate
    fpr = fp / (fp + tn)  # False positive rate

    return tpr, fpr

def plot_ROC(y_true, y_pred_li, thresholds):
    tpr_list = []
    fpr_list = []

    for y_pred in y_pred_li:
        tpr, fpr = get_tpr_and_fpr(y_true, y_pred)
        tpr_list.append(tpr)
        fpr_list.append(fpr)

    plt.figure(figsize=(5.43, 4.65)) 

    # Plotting the ROC curve
    plt.plot(fpr_list, tpr_list, marker='o', linestyle='-', label='ROC Curve', alpha=0.7, markersize=8)

    # Plotting the diagonal (random guess line)
    plt.plot([0, 1], [0, 1], 'k--', label='Random Guess')  # Diagonal line from (0, 0) to (1, 1)

    # Annotate first, middle and last point with the corresponding threshold value
    for i in [0, (len(fpr_list) // 2) - 1, len(fpr_list) - 1]:  
        plt.text(fpr_list[i], tpr_list[i], str(round(thresholds[i], 2)), 
                fontsize=9, ha='right', va='bottom', color='red')

    # Labels and legend
    plt.xlabel('False Positive Rate (FPR)')
    plt.ylabel('True Positive Rate (TPR)')
    plt.legend()

    plt.show()