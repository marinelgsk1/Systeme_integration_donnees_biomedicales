
import os

import matplotlib
matplotlib.use('Agg') 

import matplotlib.pyplot as plt


def _generate_pie_chart(labels, values, filename):
    colors = ['#4A90E2', '#7FB3E6', '#A8D0F0']
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.axis('equal')

    output_dir = 'static/plots'
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    plt.savefig(path, bbox_inches='tight', transparent=True)
    plt.close(fig)