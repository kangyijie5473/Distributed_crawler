### Server 
Server端部署在阿里云，与Client直接交互，接收Client的请求，操纵ZooKeeper集群，完成对Crawler的控制。  
在Server部署了MySQL用于存储Crawler的数据信息。  
从爬虫节点的MongoDB获取爬取的数据。  
