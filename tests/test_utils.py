"""Tests for utility modules."""

import pytest
import pandas as pd
from io import StringIO
from utils.data_processor import DataProcessor
from utils.visualizer import HeatmapVisualizer, BubbleChartVisualizer, CostEffectivenessPlot


class TestDataProcessor:
    """Test suite for DataProcessor."""

    def test_load_data_success(self, tmp_path):
        """DataProcessor should load CSV data successfully."""
        # Create test CSV
        test_data = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        test_file = tmp_path / "test_data.csv"
        test_data.to_csv(test_file, index=False)

        processor = DataProcessor(str(test_file))
        processor.load_data()
        assert processor.data is not None
        assert len(processor.data) == 3

    def test_load_data_file_not_found(self):
        """Should handle FileNotFoundError gracefully."""
        processor = DataProcessor("nonexistent_file.csv")
        processor.load_data()  # Should not raise
        assert processor.data is None

    def test_process_data_fills_missing_values(self, tmp_path):
        """process_data should fill NaN values."""
        test_data = pd.DataFrame({"col1": [1, None, 3]})
        test_file = tmp_path / "test_nan.csv"
        test_data.to_csv(test_file, index=False)

        processor = DataProcessor(str(test_file))
        processor.load_data()
        processor.process_data()
        assert processor.data["col1"].isna().sum() == 0

    def test_save_data(self, tmp_path):
        """save_data should write CSV file."""
        test_data = pd.DataFrame({"col1": [1, 2, 3]})
        input_file = tmp_path / "input.csv"
        output_file = tmp_path / "output.csv"
        test_data.to_csv(input_file, index=False)

        processor = DataProcessor(str(input_file))
        processor.load_data()
        processor.save_data(str(output_file))

        assert output_file.exists()
        loaded = pd.read_csv(output_file)
        assert len(loaded) == 3


class TestVisualizers:
    """Test suite for visualizer classes."""

    def test_heatmap_visualizer_init(self):
        """HeatmapVisualizer should initialize with correct attributes."""
        data = [[1, 2], [3, 4]]
        viz = HeatmapVisualizer(data, ["A", "B"], ["C", "D"])
        assert viz.data == data
        assert viz.x_labels == ["A", "B"]

    def test_bubble_chart_visualizer_init(self):
        """BubbleChartVisualizer should initialize correctly."""
        import pandas as pd
        data = pd.DataFrame({"x": [1, 2], "y": [3, 4], "size": [10, 20]})
        viz = BubbleChartVisualizer(data, "x", "y", "size")
        assert viz.x == "x"

    def test_cost_effectiveness_plot_init(self):
        """CostEffectivenessPlot should initialize correctly."""
        viz = CostEffectivenessPlot([100, 200], [0.05, 0.08])
        assert viz.costs == [100, 200]
        assert viz.effectiveness == [0.05, 0.08]
