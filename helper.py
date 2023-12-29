import matplotlib.pyplot as plt
from IPython import display
import datetime

plt.ion()
plt.figure(figsize=(10, 6))

# plotting training metrics
def plot(scores, mean_scores, to_save):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training Metrics')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(range(len(scores)), scores, marker='o', label='Scores', linestyle='-', linewidth=0.5)
    plt.plot(range(len(mean_scores)), mean_scores, color='orange', label='Mean Scores')
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.legend(loc='upper right', bbox_to_anchor=(1.05, 1))
    if to_save:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"training_results/training_run_{timestamp}.png"
        plt.savefig(filename, dpi=600)
        print(f"Chart saved as: {filename}")
    plt.show(block=False)
    plt.pause(.1)