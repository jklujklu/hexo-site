---
title: LNMP 安装NextCloud，搭建属于自己的网盘
date: 2020-6-5 18:38:45
categories: 
    - 教程
tags: 
    - LNMP
mp3: http://m7.music.126.net/20200615162801/a906800a4eff3d0e0efc1123b4973313/ymusic/870b/ad32/3709/aef735503eb694409ad48e3312f3e752.mp3
cover: http://api.mtyqx.cn/tapi/random.php
---
# LNMP 安装NextCloud，搭建属于自己的网盘

## LNMP环境搭建

```shell
sudo apt-get install nginx -y
sudo apt-get install mysql-server mysql-client -y
sudo apt-get install php -y
sudo apt-get install php-fpm  -y
```



---

## NextCloud搭建

### 下载

- 去官网获取在线安装包

  [NextCloud官网](https://download.nextcloud.com/server/installer/setup-nextcloud.php)

  ```shell
  cd /var/www/html
  wget https://download.nextcloud.com/server/installer/setup-nextcloud.php
  ```

- 访问网页

  > http://{your site or your domain}/setup-nextcloud.php

  如果LNMP配置正常，会出现以下界面

  ![安装初始页面](https://i.loli.net/2020/03/17/h7mqUFJbRQWGwlL.png "安装初始页面")

  ***PS：如果出现502，说明Nginx中PHP的解释器没有正确配置，请检查nginx配置中的php-fpm.sock是否正确***

### 初始化MYSQL

- 创建管理员用户

  ```mysql
  //创建用户
  create user '{yourname}'@'localhost' identified by '{yourpwd}';
  //授权
  grant all on *.* to '{yourname}'@'localhost' with grant option;
  //刷新
  flush privileges;
  ```

- 建表

  ```mysql
  create database nextcloud;
  ```



### 配置NextCloud

- 安装依赖

  点击Next，在线安装包自动检查所需依赖，如下图所示

  ![NextCloud所需依赖](https://i.loli.net/2020/03/17/2o9xAcLsZRNCY8E.png "NextCloud所需依赖")

  ```
  //安装依赖
  sudo apt-get install php-dom php-gd php-zip php-curl php-mbstring -y
  
  //文件授权
  cd /var/www/html
  chmod 777 -R .
  ```

- 配置安装路径

  依赖安装完成后，刷新网页，如果正常，会出现以下界面

  ![配置安装路径](https://i.loli.net/2020/03/17/4hQJ1Cok3ZESUrX.png "配置安装路径")

  ***P.S.1：默认安装路径为/{当前网页根目录}/nextcloud***

  **P.S.2：若要安装在根目录，修改nextcloud为.即可**

- 安装成功

  点击Next，等待片刻，出现安装成功界面

  ![安装成功](https://i.loli.net/2020/03/17/A2BReJWp6L3hYZT.png "安装成功")

- 配置数据库及管理员账户

  - 安装mysql插件（看情况）

    如果出现以下界面，说明php没有安装mysql驱动插件，从而无法访问数据库，输入以下命令安装即可

    ![缺少mysql插件](https://i.loli.net/2020/03/17/IaU7NEvde8iZC1J.png "缺少mysql插件")

    ```shell
    sudo apt-get install php-pdo-mysql -y
    ```

  自定义管理员、密码，在下方的数据库配置中输入上一步创建的数据库用户、密码、数据库

  ![配置数据库界面](https://i.loli.net/2020/03/17/E9vHIwPp4eVgbzx.png "配置数据库界面")

- 配置伪静态

  > 如果有不懂的地方可以去[nextcloud官网帮助](https://docs.nextcloud.com/server/18/admin_manual/installation/nginx.html)查看

  用户配置完成后，网页会自动跳转至主页，由于没有配置伪静态，会出现404的状态，见下图

  ![404](https://i.loli.net/2020/03/17/JaqOle9nAV8Fpju.png "404")

  进入nginx的网页配置，用下方配置替换默认配置

  ```
  upstream php-handler {
      server 127.0.0.1:9000;
      server unix:/var/run/php/php7.2-fpm.sock;
  }
  
  server {
      listen 80;
      listen [::]:80;
      server_name cloud.example.com;
      # enforce https
      return 301 https://$server_name:443$request_uri;
  }
  
  server {
      listen 443 ssl http2;
      listen [::]:443 ssl http2;
      server_name cloud.example.com;
  
      # Use Mozilla's guidelines for SSL/TLS settings
      # https://mozilla.github.io/server-side-tls/ssl-config-generator/
      # NOTE: some settings below might be redundant
      ssl_certificate /etc/ssl/nginx/cloud.example.com.crt;
      ssl_certificate_key /etc/ssl/nginx/cloud.example.com.key;
  
      # Add headers to serve security related headers
      # Before enabling Strict-Transport-Security headers please read into this
      # topic first.
      #add_header Strict-Transport-Security "max-age=15768000; includeSubDomains; preload;" always;
      #
      # WARNING: Only add the preload option once you read about
      # the consequences in https://hstspreload.org/. This option
      # will add the domain to a hardcoded list that is shipped
      # in all major browsers and getting removed from this list
      # could take several months.
      add_header Referrer-Policy "no-referrer" always;
      add_header X-Content-Type-Options "nosniff" always;
      add_header X-Download-Options "noopen" always;
      add_header X-Frame-Options "SAMEORIGIN" always;
      add_header X-Permitted-Cross-Domain-Policies "none" always;
      add_header X-Robots-Tag "none" always;
      add_header X-XSS-Protection "1; mode=block" always;
  
      # Remove X-Powered-By, which is an information leak
      fastcgi_hide_header X-Powered-By;
  
      # Path to the root of your installation
      root /var/www/nextcloud;
  
      location = /robots.txt {
          allow all;
          log_not_found off;
          access_log off;
      }
  
      # The following 2 rules are only needed for the user_webfinger app.
      # Uncomment it if you're planning to use this app.
      #rewrite ^/.well-known/host-meta /public.php?service=host-meta last;
      #rewrite ^/.well-known/host-meta.json /public.php?service=host-meta-json last;
  
      # The following rule is only needed for the Social app.
      # Uncomment it if you're planning to use this app.
      #rewrite ^/.well-known/webfinger /public.php?service=webfinger last;
  
      location = /.well-known/carddav {
        return 301 $scheme://$host:$server_port/remote.php/dav;
      }
      location = /.well-known/caldav {
        return 301 $scheme://$host:$server_port/remote.php/dav;
      }
  
      # set max upload size
      client_max_body_size 512M;
      fastcgi_buffers 64 4K;
  
      # Enable gzip but do not remove ETag headers
      gzip on;
      gzip_vary on;
      gzip_comp_level 4;
      gzip_min_length 256;
      gzip_proxied expired no-cache no-store private no_last_modified no_etag auth;
      gzip_types application/atom+xml application/javascript application/json application/ld+json application/manifest+json application/rss+xml application/vnd.geo+json application/vnd.ms-fontobject application/x-font-ttf application/x-web-app-manifest+json application/xhtml+xml application/xml font/opentype image/bmp image/svg+xml image/x-icon text/cache-manifest text/css text/plain text/vcard text/vnd.rim.location.xloc text/vtt text/x-component text/x-cross-domain-policy;
  
      # Uncomment if your server is build with the ngx_pagespeed module
      # This module is currently not supported.
      #pagespeed off;
  
      location / {
          rewrite ^ /index.php;
      }
  
      location ~ ^\/(?:build|tests|config|lib|3rdparty|templates|data)\/ {
          deny all;
      }
      location ~ ^\/(?:\.|autotest|occ|issue|indie|db_|console) {
          deny all;
      }
  
      location ~ ^\/(?:index|remote|public|cron|core\/ajax\/update|status|ocs\/v[12]|updater\/.+|oc[ms]-provider\/.+)\.php(?:$|\/) {
          fastcgi_split_path_info ^(.+?\.php)(\/.*|)$;
          set $path_info $fastcgi_path_info;
          try_files $fastcgi_script_name =404;
          include fastcgi_params;
          fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
          fastcgi_param PATH_INFO $path_info;
          fastcgi_param HTTPS on;
          # Avoid sending the security headers twice
          fastcgi_param modHeadersAvailable true;
          # Enable pretty urls
          fastcgi_param front_controller_active true;
          fastcgi_pass php-handler;
          fastcgi_intercept_errors on;
          fastcgi_request_buffering off;
      }
  
      location ~ ^\/(?:updater|oc[ms]-provider)(?:$|\/) {
          try_files $uri/ =404;
          index index.php;
      }
  
      # Adding the cache control header for js, css and map files
      # Make sure it is BELOW the PHP block
      location ~ \.(?:css|js|woff2?|svg|gif|map)$ {
          try_files $uri /index.php$request_uri;
          add_header Cache-Control "public, max-age=15778463";
          # Add headers to serve security related headers (It is intended to
          # have those duplicated to the ones above)
          # Before enabling Strict-Transport-Security headers please read into
          # this topic first.
          #add_header Strict-Transport-Security "max-age=15768000; includeSubDomains; preload;" always;
          #
          # WARNING: Only add the preload option once you read about
          # the consequences in https://hstspreload.org/. This option
          # will add the domain to a hardcoded list that is shipped
          # in all major browsers and getting removed from this list
          # could take several months.
          add_header Referrer-Policy "no-referrer" always;
          add_header X-Content-Type-Options "nosniff" always;
          add_header X-Download-Options "noopen" always;
          add_header X-Frame-Options "SAMEORIGIN" always;
          add_header X-Permitted-Cross-Domain-Policies "none" always;
          add_header X-Robots-Tag "none" always;
          add_header X-XSS-Protection "1; mode=block" always;
  
          # Optional: Don't log access to assets
          access_log off;
      }
  
      location ~ \.(?:png|html|ttf|ico|jpg|jpeg|bcmap)$ {
          try_files $uri /index.php$request_uri;
          # Optional: Don't log access to other assets
          access_log off;
      }
  }
  ```

  ***P.S.1：上方配置默认采用https加密通信，若要使用http访问，需修改以下信息***

  ```
  server {	--->	删除 
      listen 80;	--->	删除 
      listen [::]:80;	--->	删除 
      server_name cloud.example.com;	--->	删除 
      # enforce https		--->	删除 
      return 301 https://$server_name:443$request_uri;	--->	删除 
  }		--->	删除 
  listen 443 ssl http2;		--->  listen 80
  listen [::]:443 ssl http2;	--->  listen [::]:80
  ssl_certificate /etc/ssl/nginx/cloud.example.com.crt;			--->	删除 
  ssl_certificate_key /etc/ssl/nginx/cloud.example.com.key;		--->	删除 
  fastcgi_param HTTPS on;		--->	删除
  ```

  ***P.S.2：如果出现404说明，伪静态设置不正确，若果出现502，说明php-fpm设置不正确***

- 重启nginx服务

  刷新网页，大功告成！

  ![](https://i.loli.net/2020/03/17/QAG7fvujxXNnw4p.png)