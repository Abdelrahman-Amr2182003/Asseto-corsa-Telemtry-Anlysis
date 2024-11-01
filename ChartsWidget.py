from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtChart import *


import os
import pandas as pd

class ChartUpdateSignal(QObject):
    data_received = pyqtSignal(float, float)


class LineChart(QChart):
    def __init__(self, title):
        super().__init__()
        title_font = QFont("Arial", 16)  # Change the font family and size as needed
        title_font.setBold(True)  # Make the font bold
        self.setTitleFont(title_font)
        self.title = title
        self.axis_format = None
        self.setTitle(title)

        self.chart_view = QChartView(self)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMouseTracking(True)
        self.chart_view.setRubberBand(QChartView.HorizontalRubberBand)
        self.setAnimationOptions(QChart.SeriesAnimations)

        #self.setTheme(QChart.ChartThemeBlueCerulean)
        self.update_signal = ChartUpdateSignal()
        self.update_signal.data_received.connect(self.update_chart)

    def update_chart(self, x, y):
        # Assuming your series is stored as self.line_series
        self.line_series.append(x, y)
        self.axisX().setMax(x + 10)  # Adjust as needed
        self.axisY().setMax(max(self.axisY().max(), y) + 10)  # Adjust as needed

    def is_numerical(self,col):
        for i in col:
            i = str(i)
            if i!="" and i is not None:
                if self.isfloat(i):
                    pass
                else:
                    return False
        return True
    def isfloat(self,num):
        try:
            float(num)
            return True
        except ValueError:
            return False



    def create_line_chart(self,data):
        for key in list(data.keys()):
            values = data[key][1]
            date_times = data[key][0]

            self.line_series = QLineSeries()
            self.line_series.setName(key)

            for i, value in enumerate(values):
                self.line_series.append(float(date_times[i]), float(value))
            self.addSeries(self.line_series)
            self.line_series.setPointsVisible(True)
            self.line_series.hovered.connect(self.on_point_hovered)
            self.line_series.attachAxis(self.axisX())

            self.line_series.attachAxis(self.axisY())

        #line_series.setName(class_name)  # Set label for the line series
    def on_point_hovered(self, point, state):
        if state:
            value = point.y()
            x_axis = point.x()
            self.setTitle(f"Hovered Point: Value={value:.2f}, x_axis={x_axis:.2f}")

        else:
            self.setTitle(self.title)
    def get_chart(self):
        chart_view = QChartView(self)
        #chart_view.setMouseTracking(True)
        chart_view.setRenderHint(QPainter.Antialiasing)
        self.legend().setVisible(True)
        chart_view.setRubberBand(QChartView.HorizontalRubberBand)

        return chart_view
