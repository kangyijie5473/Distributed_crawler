package test;
import java.awt.Graphics;
import java.awt.Color;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import javax.swing.JFrame;
 
public class JFrameDraw2 extends JFrame{
    public JFrameDraw2(){
        super("Java画图程序");
        setSize(600,500);  //设置窗口尺寸
        setVisible(true);  //设置窗口为可视
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);  //关闭窗口时退出程序
        addMouseListener(new MouseAdapter(){
            public void mouseClicked(MouseEvent e){
                JFrameDraw2.this.repaint();
            }
        });
    }
     
    java.util.Random rnd = new java.util.Random();
    public void paint(Graphics g){
        super.paint(g);
        int x1=150, y1=200,  x2=60, y2=60;
        for(int i=0; i<20; i++){
            int ir=rnd.nextInt(0xff);
            int ig=rnd.nextInt(0xff);
            int ib=rnd.nextInt(0xff);
            g.setColor(new Color(ir,ig,ib));
            g.drawRect(x1, y1, x2, y2);
            g.drawOval(x1+260, y1, x2, y2);
            try{Thread.sleep(100);}catch(Exception eex){}
            x1-=5;
            y1-=5;
            x2+=10;
            y2+=10;
             
        }
    }
     
    public static void main(String[] args){
        new JFrameDraw2();
    }
}