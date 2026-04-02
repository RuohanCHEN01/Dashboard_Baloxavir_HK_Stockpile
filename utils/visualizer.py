import plotly.graph_objects as go
import matplotlib.pyplot as plt

class HeatmapVisualizer:
    def __init__(self, data, x_labels, y_labels, title='Heatmap'):
        self.data = data
        self.x_labels = x_labels
        self.y_labels = y_labels
        self.title = title

    def plot(self):
        fig = go.Figure(data=go.Heatmap(z=self.data, x=self.x_labels, y=self.y_labels, colorscale='Viridis'))
        fig.update_layout(title=self.title)
        fig.show()

class BubbleChartVisualizer:
    def __init__(self, data, x, y, size, title='Bubble Chart'):
        self.data = data
        self.x = x
        self.y = y
        self.size = size
        self.title = title

    def plot(self):
        fig = go.Figure(data=go.Scatter(
            x=self.data[self.x], 
            y=self.data[self.y], 
            mode='markers',
            marker=dict(size=self.data[self.size]),
        ))
        fig.update_layout(title=self.title)
        fig.show()

class KPIVisualizer:
    def __init__(self, kpi_value, kpi_label, title='KPI Card'):
        self.kpi_value = kpi_value
        self.kpi_label = kpi_label
        self.title = title

    def plot(self):
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f'{self.kpi_label}: {self.kpi_value}', fontsize=24,
                ha='center', va='center', bbox=dict(facecolor='white', alpha=0.8))
        ax.axis('off')
        plt.title(self.title)
        plt.show()

class CostEffectivenessPlot:
    def __init__(self, costs, effectiveness, title='Cost-Effectiveness Plot'):
        self.costs = costs
        self.effectiveness = effectiveness
        self.title = title

    def plot(self):
        plt.scatter(self.costs, self.effectiveness)
        plt.title(self.title)
        plt.xlabel('Costs')
        plt.ylabel('Effectiveness')
        plt.show()