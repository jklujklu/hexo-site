---
title: LNMP 环境搭建
date: 2020-6-6 18:38:45
categories: 
    - 教程
tags: 
    - LNMP
mp3: http://m7.music.126.net/20200615162801/a906800a4eff3d0e0efc1123b4973313/ymusic/870b/ad32/3709/aef735503eb694409ad48e3312f3e752.mp3
cover: http://api.mtyqx.cn/tapi/random.php
---
# LNMP环境搭建

***以下所有操作均在Ubuntu环境下进行***

## Nginx安装

### apt方式进行安装

```shell
sudo apt-get install nginx -y
```

安装成功后，浏览器中输入IP，可以看到nginx已经启动，如果没有出现下面的画面，输入以下命令进行手动启动

```shell
sudo systemctl start nginx		# 启动服务
sudo systemctl stop nginx		# 关闭服务
sudo systemctl status nginx		# 服务状态
sudo systemctl restart nginx	# 重启服务
```

![image.png](https://i.loli.net/2020/03/13/bq2avxLAlB9fzEQ.png "默认的80端口")

---

### 更改监听端口（可选）

```shell
cd /etc/nginx/sites-available
vim default

# 根据需求修改对应配置即可

server {
	listen 80;			# ipv4地址
	listen [::]:80;		# ipv6地址

	server_name example.com;	

	root /var/www/example.com;	# 网站根目录
	index index.html;	# 首页类型，如果是php动态生成的网页，需要增加index.php
	location / {
		# 伪静态，根据url去根目录对应的位置寻找文件，如果找不到，其在url的下一层目录查询，如果还没有，就返回最后一个参数，即404
		try_files $uri $uri/ =404;
	}
}
```

修改端口为8080，开启ufw防火墙，允许外界访问8080端口，最后可以得到下面的界面

```shell
sudo ufw enable			# 开启防火墙
sudo ufw allow 8080		# 放行8080端口
sudo ufw status			# 查看防火墙状态
```

![image.png](https://i.loli.net/2020/03/13/VBAtmacDMzIe1OF.png "8080端口")

![image.png](https://i.loli.net/2020/03/13/WVHclhsz5x6EoGu.png "防火墙状态")

---

### 监听多个端口（可选）

```shell
cd /etc/nginx/sites-available
cp default new	# 将默认页面复制一份形成新的页面
# 在新的页面中根据上方描述，配置新的端口、根目录、伪静态等
...
cd ../sites-enabled
ln -s ../sites-available/ne ne	# 创建符号链接，将其链接到site-enabled文件夹
ufw allow {port}	# 放行指定的端口
systemctl restart nginx	# 重启服务
```

## MYSQL安装

### apt方式进行安装

```shell
# mysql-server 针对mysql服务器，主要用于托管数据库，负责数据库底层的文件组织等工作
# mysql-client 针对mysql的客户端，主要用于连接数据库，并进行查询更新等操作
# 如果只需要连接远程数据库，并进行查询等操作，则只需要安装mysql-client
sudo apt-get install mysql-server mysql-client -y
```

---

### 创建用户并授权（可选）

```mysql
# 使用空密码进入mysql终端
mysql -uroot -p
# 创建用户
CREATE USER 'yourname'@'%' IDENTIFIED BY 'yourpwd';
# 用户授权
GRANT ALL ON *.* TO 'yournam'@'%';
```

---

### 开启数据库远程访问（可选）

```mysql
# 查询所有用户的信息
SELECT DISTINCT CONCAT('User: ''',user,'''@''',host,''';') AS query FROM mysql.user;
# 找到要开启远程链接的用户，确保其Host属性为%
# 确保格式为User: 'yourname'@'%';

# 如果Host不为%执行下方操作
use mysql;
update user set Host = '%'  where User = '{yourname}';
flush privileges;

vim /etc/mysql/mysql.conf.d/mysqld.cnf
# 找到下方的语句，将其注释掉
bind-address          = 127.0.0.1

ufw allow 3306 # 放行3306
systemctl restart mysql	# 重启mysql
```

---

## PHP安装

### apt方式进行安装

```shell
sudo apt-get install php -y	# 安装php
sudo apt-get install php-fpm -y	# 安装php-fpm，CGI解释器进程管理工具
# 安装完成后输入以下命令查看php版本信息
php -v
```

版本信息返回如下，即为安装成功

![php安装完成](https://i.loli.net/2020/03/13/tNgksyAUF9TXoz6.png "php安装完成")

### 配置web php环境

```shell
# 1. 将原来的首页重命名
mv /var/www/html/index.html  /var/www/html/~index.html 
# 2. 创建新的由php驱动的首页
vim /var/www/html/index.php
# 输入以下信息
<?php
echo phpinfo();
?>

whereis php-fpm
# > php-fpm: /usr/sbin/php-fpm7.2

# 3. 链接php解释器，同时检查一下index中是否存在index.php，若不存在，请添加
vim /etc/nginx/sites-available/default

# 找到下方文本将其修改为下方图片显示的样子，其中红框中的php-fpm版本改为上方命令显示的版本即可
#location ~ \.php$ {
#        include snippets/fastcgi-php.conf;
#
#       # With php-fpm (or other unix sockets)
#        fastcgi_pass unix:/var/run/php/php7.0-fpm.sock;
#       # With php-cgi (or other tcp sockets):
#       fastcgi_pass 127.0.0.1:9000;
#}

# 4. 重启服务
systemctl restart nginx
```

![php-fpm](https://i.loli.net/2020/03/13/YM17FbNHm5Ej6To.png "php-fpm")

![phpinfo](https://i.loli.net/2020/03/13/QXrEPgptWUyZRa4.png "phpinfo")

---

<center>
    至此，LNMP环境搭建完成*^____^*
</center>
---

---

---

## 安装phpmyadmin管理数据库（可选）

```shell
# 安装，期间会让你选择服务器，直接选apache即可，然后自己设置密码
sudo apt-get install phpmyadmin -y
# 进入网站根目录
cd /var/www/html
# 创建软连接
ln -s /usr/share/phpmyadmin
```

浏览器输入网站进入phpmyadmin登陆界面，若安装成功，显示如下

![phpmyadmin](https://i.loli.net/2020/03/13/H2fyUB9rvOwgpVE.png "phpmyadmin")

***用户名为phpmyadmin，密码为自己设置的密码***

![dashboard](https://i.loli.net/2020/03/13/iC2tdjbxnKEmReP.png "dashboard")

<center>
    接下来愉快的操作数据库吧( •̀ ω •́ )✧
</center>
## 实践（安装Chevereto图床）

- 获取源文件

  ```shell
  # 以默认根目录/var/www/html为例
  cd /var/www/html
  # 获取图床程序（二选一）
  wget https://github.com/Chevereto/Chevereto-Free/archive/1.1.4.zip
  unzip 1.1.4.zip
  
  # 直接下载Chevereto官网的installer自动安装（二选一）
  wget https://chevereto.com/download/file/installer
  mv installer installer.php
  # 将其解压至网站根目录
  ...
  
  chmod 777 -r *	# 赋予权限
  
  ```

- nginx伪静态设置

  ```shell
  cd /etc/nginx/sites-available
  vim default
  
  # 在server标签中添加一下代码，注意如果和原来的伪静态规则冲突，请将原来的删除或进行合并
  # Image not found replacement
  location ~* (jpe?g|png|gif|webp) {
          log_not_found off;
          error_page 404 /content/images/system/default/404.gif;
  }
  
  # CORS header (avoids font rendering issues)
  location ~ \.(ttf|ttc|otf|eot|woff|woff2|font.css|css|js)$ {
          add_header Access-Control-Allow-Origin "*";
  }
  
  # Pretty URLs
  location / {
          index index.php;
          try_files $uri $uri/ /index.php$is_args$query_string;
  }
  ```

- 配置php插件

  ```shell
  sudo apt-get install php-curl php-zip php-pdo-mysql php-mbstring php-gd -y
  
  vim /etc/php/7.2/cli/php.ini
  
  # 找到一下几项，将前面的,去除
  ;extension=pdo_mysql
  ;extension=mbstring
  ;extension=pdo_mysql
  ```

- 重启nginx

  ```shell
  systemctl restart nginx
  ```

- 大功告成

  如果是官网的安装包，会出现以下界面

  ![](https://i.loli.net/2020/03/13/OSd1iW8jhFQmKq9.png)

  如果是完整的源码，会出现以下界面

  ![](https://i.loli.net/2020/03/13/zdekF2YcZ5uJ7Nv.png)

<center>
    Enjoy Yourself（￣︶￣）↗　
</center>

