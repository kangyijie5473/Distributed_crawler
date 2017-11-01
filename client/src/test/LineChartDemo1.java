package test;
import java.awt.BasicStroke;  
import java.awt.Color;  
import java.awt.Dimension;  
import java.awt.geom.Ellipse2D;  
import java.io.File;  
import java.io.IOException;  
import java.text.DecimalFormat;  
import java.util.Random;  
  
import javax.swing.JPanel;  
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
import org.jfree.data.category.CategoryDataset;  
import org.jfree.data.category.DefaultCategoryDataset;  
import org.jfree.ui.ApplicationFrame;  
import org.jfree.ui.RefineryUtilities;  
  
public class LineChartDemo1 extends ApplicationFrame {  
  
    private static final long serialVersionUID = -6354350604313079793L;  
    /* synthetic */static Class class$demo$LineChartDemo1;  
  
    public LineChartDemo1(String string) {  
         super(string);  
        JPanel jpanel = createDemoPanel();  
        jpanel.setPreferredSize(new Dimension(500, 270));  
         setContentPane(jpanel);  
    }  
  
      
      
    /** 
     * 如何区分不同的图例：根据DefaultCategoryDataset.addValue()的第二个参数是否相同来区分。 
     * 同一个图例的数据的添加顺序影响最终的显示；不同图例的数据的添加顺序不影响最终的显示。 
     * @return 
     */  
    private static CategoryDataset createDataset() {  
        DefaultCategoryDataset defaultcategorydataset = new DefaultCategoryDataset();  
        //defaultcategorydataset.addValue()的参数解析：（数值，图例名，横坐标值）  
/*     
        //添加数据方法1 
        //图例1 
        defaultcategorydataset.addValue(212.0, "First", "1001.0"); 
         defaultcategorydataset.addValue(504.0, "First", "1001.1"); 
        defaultcategorydataset.addValue(1520.0, "First", "1001.2"); 
 
        //图例2 
        defaultcategorydataset.addValue(712.0, "Second", "1001.0"); 
         defaultcategorydataset.addValue(1204.0, "Second", "1001.1"); 
        defaultcategorydataset.addValue(1820.0, "Second", "1001.2");         
/*/  
//*  
        //添加数据方法2  
        //实验随机数来生成测试结果  
        Random random = new Random(12345);   
  
        //图例1，40个数据  
        for(int i=0;i<40;i++){  
            defaultcategorydataset.addValue(random.nextInt(100000),  
                    "First",String.valueOf(1000+i) );  
        }  
        //图例2，40个数据  
        for (int i = 0; i < 40; i++) {  
            defaultcategorydataset.addValue(random.nextInt(100000),  
                    "Second", String.valueOf(1000 + i));  
        }  
//*/          
          
        return defaultcategorydataset;  
    }  
  
    private static JFreeChart createChart(CategoryDataset categorydataset) {  
        JFreeChart jfreechart = ChartFactory.createLineChart(  
                "jfreechart test",// 图表标题  
                "X", // 主轴标签（x轴）  
                "Y",// 范围轴标签（y轴）  
                categorydataset, // 数据集  
                PlotOrientation.VERTICAL,// 方向  
                false, // 是否包含图例  
                true, // 提示信息是否显示  
                false);// 是否使用urls  
           
        // 改变图表的背景颜色  
        jfreechart.setBackgroundPaint(Color.white);  
          
        CategoryPlot categoryplot = (CategoryPlot) jfreechart.getPlot();  
        categoryplot.setBackgroundPaint(Color.lightGray);  
        categoryplot.setRangeGridlinePaint(Color.white);  
        categoryplot.setRangeGridlinesVisible(false);  
  
        //修改范围轴。 我们将默认刻度值 （允许显示小数） 改成只显示整数的刻度值。  
        NumberAxis numberaxis = (NumberAxis) categoryplot.getRangeAxis();  
        numberaxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());  
          
        // 设置X轴上的Lable让其45度倾斜   
        CategoryAxis domainAxis = categoryplot.getDomainAxis();  
        domainAxis.setCategoryLabelPositions(CategoryLabelPositions.UP_45); // 设置X轴上的Lable让其45度倾斜       
         domainAxis.setLowerMargin(0.0);   // 设置距离图片左端距离   
         domainAxis.setUpperMargin(0.0);  // 设置距离图片右端距离   
          
            
            
        LineAndShapeRenderer lineandshaperenderer = (LineAndShapeRenderer) categoryplot  
                .getRenderer();  
        lineandshaperenderer.setShapesVisible(true);  
        lineandshaperenderer.setDrawOutlines(true);  
        lineandshaperenderer.setUseFillPaint(true);  
        lineandshaperenderer.setBaseFillPaint(Color.white);  
        lineandshaperenderer.setSeriesStroke(0, new BasicStroke(3.0F));  
        lineandshaperenderer.setSeriesOutlineStroke(0, new BasicStroke(2.0F));  
        lineandshaperenderer.setSeriesShape(0, new Ellipse2D.Double(-5.0, -5.0,  
                10.0, 10.0));  
        lineandshaperenderer.setItemMargin(0.4); //设置x轴每个值的间距（不起作用？？）  
          
        // 显示数据值  
        DecimalFormat decimalformat1 = new DecimalFormat("##.##");// 数据点显示数据值的格式  
        lineandshaperenderer.setBaseItemLabelGenerator(new StandardCategoryItemLabelGenerator(  
                "{2}", decimalformat1));//  设置数据项标签的生成器  
        lineandshaperenderer.setBaseItemLabelsVisible(true);// 基本项标签显示  
        lineandshaperenderer.setBaseShapesFilled(true);// 在数据点显示实心的小图标  
                  
          
        return jfreechart;  
    }  
  
    public static JPanel createDemoPanel() {  
        JFreeChart jfreechart = createChart(createDataset());  
  
        try {  
            ChartUtilities.saveChartAsJPEG(  
                    new File("1.png"), //文件保存物理路径包括路径和文件名   
                 //    1.0f,    //图片质量 ，0.0f~1.0f  
                     jfreechart, //图表对象   
                    1024,   //图像宽度 ，这个将决定图表的横坐标值是否能完全显示还是显示省略号  
                    768);  
        } catch (IOException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        }    //图像高度   
                   
        return new ChartPanel(jfreechart);  
    }  
  
    public static void main(String[] strings) {  
        LineChartDemo1 linechartdemo1 = new LineChartDemo1(  
                "JFreeChart - Line Chart Demo 1");  
        linechartdemo1.pack();  
        RefineryUtilities.centerFrameOnScreen(linechartdemo1);  
        linechartdemo1.setVisible(true);  
    }  
  
    /* synthetic */  
    static Class class$(String string) {  
        Class var_class;  
        try {  
            var_class = Class.forName(string);  
        } catch (ClassNotFoundException classnotfoundexception) {  
            throw new NoClassDefFoundError(classnotfoundexception.getMessage());  
        }  
        return var_class;  
    }  
}  