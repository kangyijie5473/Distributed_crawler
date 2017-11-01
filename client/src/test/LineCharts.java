package test;
import java.awt.Font;
import javax.swing.JPanel;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.CategoryAxis;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.CategoryPlot;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.title.LegendTitle;
import org.jfree.data.category.DefaultCategoryDataset;
import org.jfree.ui.ApplicationFrame;
import org.jfree.ui.RefineryUtilities;
public class LineCharts extends ApplicationFrame {
public LineCharts(String s) {
   super(s);
   setContentPane(createDemoLine());
}
public static void main(String[] args) {
   LineCharts fjc = new LineCharts("折线图");
   fjc.pack();
   RefineryUtilities.centerFrameOnScreen(fjc);
   fjc.setVisible(true);
}
// 生成显示图表的面板
public static JPanel createDemoLine() {
   JFreeChart jfreechart = createChart(createDataset());
   return new ChartPanel(jfreechart);
}
// 生成图表主对象JFreeChart
public static JFreeChart createChart(DefaultCategoryDataset linedataset) {
   // 定义图表对象
   JFreeChart chart = ChartFactory.createLineChart("折线图", // chart title
     "时间", // domain axis label
     "销售额(百万)", // range axis label
     linedataset, // data
     PlotOrientation.VERTICAL, // orientation
     true, // include legend
     true, // tooltips
     false // urls
     );
   CategoryPlot plot = chart.getCategoryPlot();  
   // 设置图示字体 
   chart.getTitle().setFont(new Font("宋体", Font.BOLD, 22));   
   //设置横轴的字体
   CategoryAxis categoryAxis = plot.getDomainAxis();
   categoryAxis.setLabelFont(new Font("宋体", Font.BOLD, 22));//x轴标题字体 
   categoryAxis.setTickLabelFont(new Font("宋体", Font.BOLD, 18));//x轴刻度字体
   //以下两行 设置图例的字体
   LegendTitle legend = chart.getLegend(0);
   legend.setItemFont(new Font("宋体", Font.BOLD, 14));
   //设置竖轴的字体
   NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
   rangeAxis.setLabelFont(new Font("宋体" , Font.BOLD , 22)); //设置数轴的字体
   rangeAxis.setTickLabelFont(new Font("宋体" , Font.BOLD , 22));
  
   rangeAxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());//去掉竖轴字体显示不全
   rangeAxis.setAutoRangeIncludesZero(true);
   rangeAxis.setUpperMargin(0.20);
   rangeAxis.setLabelAngle(Math.PI / 2.0);
   return chart;
}
// 生成数据
public static DefaultCategoryDataset createDataset() {
   DefaultCategoryDataset linedataset = new DefaultCategoryDataset();
   // 各曲线名称
   String series1 = "冰箱";
   String series2 = "彩电";
   String series3 = "洗衣机";
   // 横轴名称(列名称)
   String type1 = "1月";
   String type2 = "2月";
   String type3 = "3月";
   linedataset.addValue(0.0, series1, type1);
   linedataset.addValue(4.2, series1, type2);
   linedataset.addValue(3.9, series1, type3);
   linedataset.addValue(1.0, series2, type1);
   linedataset.addValue(5.2, series2, type2);
   linedataset.addValue(7.9, series2, type3);
   linedataset.addValue(2.0, series3, type1);
   linedataset.addValue(9.2, series3, type2);
   linedataset.addValue(8.9, series3, type3);
   return linedataset;
}
}