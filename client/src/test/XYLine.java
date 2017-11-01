package test;

import java.awt.Font;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartFrame;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.StandardChartTheme;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

public class XYLine {
  public static void main(String[] args) {
    StandardChartTheme mChartTheme = new StandardChartTheme("CN");
    mChartTheme.setLargeFont(new Font("黑体", Font.BOLD, 20));
    mChartTheme.setExtraLargeFont(new Font("宋体", Font.PLAIN, 15));
    mChartTheme.setRegularFont(new Font("宋体", Font.PLAIN, 15));
    ChartFactory.setChartTheme(mChartTheme);		
    XYSeriesCollection mCollection = GetCollection();
    JFreeChart mChart = ChartFactory.createXYLineChart(
        "折线图",
        "X",
        "Y",				
        mCollection,
        PlotOrientation.VERTICAL,
        true, 
        true, 
        false);
    ChartFrame mChartFrame = new ChartFrame("折线图", mChart);
    mChartFrame.pack();
    mChartFrame.setVisible(true);

  }	
  public static XYSeriesCollection GetCollection()
  {
    XYSeriesCollection mCollection = new XYSeriesCollection();
    XYSeries mSeriesFirst = new XYSeries("First");
    mSeriesFirst.add(1.0D, 1.0D);
      mSeriesFirst.add(2D, 4D);
      mSeriesFirst.add(3D, 3D);
      mSeriesFirst.add(4D, 5D);
      mSeriesFirst.add(5D, 5D);
      mSeriesFirst.add(6D, 7D);
      mSeriesFirst.add(7D, 7D);
      mSeriesFirst.add(8D, 8D);
      XYSeries mSeriesSecond = new XYSeries("Second");
      mSeriesSecond.add(1.0D, 5D);
      mSeriesSecond.add(2D, 7D);
      mSeriesSecond.add(3D, 6D);
      mSeriesSecond.add(4D, 8D);
      mSeriesSecond.add(5D, 4D);
      mSeriesSecond.add(6D, 4D);
      mSeriesSecond.add(7D, 2D);
      mSeriesSecond.add(8D, 1.0D);
    mCollection.addSeries(mSeriesFirst);
    mCollection.addSeries(mSeriesSecond);
    return mCollection;
  }

}
