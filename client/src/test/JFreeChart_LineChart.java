package test;  
  
import java.awt.Color;
import java.awt.Font;  
import java.io.FileOutputStream;  
import java.io.IOException;  
import java.util.Random;

import javax.swing.JFrame;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.ChartUtilities;  
import org.jfree.chart.JFreeChart;  
import org.jfree.chart.axis.CategoryAxis;  
import org.jfree.chart.axis.CategoryLabelPositions;  
import org.jfree.chart.axis.NumberAxis;  
import org.jfree.chart.labels.StandardCategoryItemLabelGenerator;  
import org.jfree.chart.plot.CategoryPlot;  
import org.jfree.chart.plot.PlotOrientation;  
import org.jfree.chart.renderer.category.LineAndShapeRenderer;  
import org.jfree.chart.title.TextTitle;  
import org.jfree.data.category.DefaultCategoryDataset;  
  
/** 
 *  
 * @ClassName: JFreeChart_LineChart 
 * @author xialong 
 * @date Jan 25, 2011 5:30:04 PM 
 * @Description: 
 *     JFreeChart生成折线图 
 */  
public class JFreeChart_LineChart {  
      
    public static void main(String[] arg){  
        try {  
            print();  
        } catch (IOException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        }  
    }  
      
    /** 
     * 输出图片 
     * @throws IOException 
     */  
    public static void print() throws IOException{
    	JFrame a = new JFrame();
    	a.setContentPane(new ChartPanel(getJFreeChart()));
    	a.setVisible(true);
    }  
  
    /** 
     * 产生JFreeChart对象 
     *  
     * @return 
     */  
    public static JFreeChart getJFreeChart() {  
        JFreeChart imgChart=null;  
        // JFreeChart对象 参数：标题，目录轴显示标签，数值轴显示标签，数据集，是否显示图例，是否生成工具，是否生成URL连接  
          
        //平面  
        imgChart = ChartFactory.createLineChart("", "X轴", "Y轴",  
                getDataSet(), PlotOrientation.VERTICAL, true, true, false);  
        //3D  
//      imgChart = ChartFactory.createLineChart3D("", "X轴", "Y轴",  
//              getDataSet(), PlotOrientation.VERTICAL, true, true, false);  
          
        imgChart.setBackgroundPaint(Color.white);  
        imgChart.setBorderVisible(true);// 边框可见  
        // 解决曲线图片标题中文乱码问题  
        //解决图表底部中文乱码问题  
        imgChart.getLegend().setItemFont(new Font("宋体", Font.PLAIN, 12));  
        CategoryPlot categoryplot = (CategoryPlot) imgChart.getPlot();  
        categoryplot.setBackgroundPaint(Color.lightGray);  
        categoryplot.setRangeGridlinePaint(Color.white);  
          
        // Y轴  
        NumberAxis numberaxis = (NumberAxis) categoryplot.getRangeAxis();  
        setNumberAxis(numberaxis);  
          
        // x轴  
        CategoryAxis domainAxis = (CategoryAxis) categoryplot.getDomainAxis();  
        setDomainAxis(domainAxis);  
          
          
        LineAndShapeRenderer lineandshaperenderer = (LineAndShapeRenderer) categoryplot  
                .getRenderer();// 数据点  
        // series 点（即数据点）可见  
        lineandshaperenderer.setBaseShapesVisible(true);  
        // 显示数据点的数据  
        lineandshaperenderer  
                .setBaseItemLabelGenerator(new StandardCategoryItemLabelGenerator());   
        // 显示折线图点上的数据  
        lineandshaperenderer.setBaseItemLabelsVisible(true);  
        return imgChart;  
    }  
      
    /** 
     * 设置X轴 
     * @param domainAxis 
     */  
    private static void setDomainAxis(CategoryAxis domainAxis){  
        // 解决x轴坐标上中文乱码  
        domainAxis.setTickLabelFont(new Font("sans-serif", Font.PLAIN, 11));  
        // 解决x轴标题中文乱码  
        domainAxis.setLabelFont(new Font("宋体", Font.PLAIN, 14));  
        // 用于显示X轴刻度  
        domainAxis.setTickMarksVisible(true);  
        //设置X轴45度  
        domainAxis.setCategoryLabelPositions(CategoryLabelPositions.UP_45);  
    }  
      
    /** 
     * 设置Y轴 
     * @param numberAxis 
     */  
    private static void setNumberAxis(NumberAxis numberaxis){  
        numberaxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());  
        // 是否显示零点  
        numberaxis.setAutoRangeIncludesZero(true);  
        numberaxis.setAutoTickUnitSelection(false);  
        // 解决Y轴标题中文乱码  
        numberaxis.setLabelFont(new Font("sans-serif", Font.PLAIN, 14));  
        // numberaxis.setTickUnit(new NumberTickUnit(10000));//Y轴数据间隔  
    }  
      
    /** 
     * 产生数据源 
     *  
     * @return 
     */  
    private static DefaultCategoryDataset getDataSet() {  
        DefaultCategoryDataset defaultcategorydataset = new DefaultCategoryDataset();  
        int i = 0;  
        Random rand = new Random();  
        while (i < 3) {  
            for (int j = 1; j < 10; j++) {  
                defaultcategorydataset.addValue(rand.nextInt(10), "series" + i,  
                        "x轴"+j);  
            }  
            i++;  
        }  
        return defaultcategorydataset;  
    }  
}  