package test;

public class Tel {
	public static void main(String[] args){
		int[] source= new int[]{9,2,7,1,0,5};
		int[] index = new int[]{3,5,3,1,0,4,2,0,4,2,0};
		String telphone="";
		for(int i:index){
			telphone += source[i];
		}
		System.out.println(telphone);
	}
}
