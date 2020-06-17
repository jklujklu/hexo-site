---
title: GlidedSky 爬虫挑战-JS加密1
date: 2020-6-2 18:38:45
categories: 
    - 爬虫
tags: 
    - Python
    - GlidedSky
---
# GlidedSky 爬虫挑战-JS加密1

## 实验环境

1. Python 3.8.1
2. Pycharm 2019.3

## 相关依赖

1. requests（发送http请求）
2. BeautifulSoup（document解析）
3. fake-useragent（伪装请求头）

## 实现过程

### 1. 网页分析

- 待爬网页介绍

  [http://glidedsky.com/level/web/crawler-javascript-obfuscation-1](http://glidedsky.com/level/web/crawler-javascript-obfuscation-1)

  > 爬虫想要的数据可能是直接从HTML源码里面拿到，也可能是从AJAX请求里面拿到。这取决于开发者的方案。
  >
  > 由JS脚本发起的AJAX请求，由于经过了一道JS，那就可以有很多套路了。比如说对数据本身加解密，对请求增加验证签名。
  >
  > 因此面对此种加密，直接**用浏览器的开发者模式找出相应的js加密算法**即可直接调用api获得数据

---



- F12进行抓包，可以看到所有的数据均通过AJAX异步加载，因此要想获取数据，直接GET相对应的API即可

  ![image.png](https://i.loli.net/2020/03/12/IwFgpBVrX5u7dZC.png "image.png")

---



- 分析上方获取的API接口的参数，可以看出此API进行了加密，每次请求需要对应的签名sign，接下来只要分析出生成sign的js算法即可

  > http://glidedsky.com/api/level/web/crawler-javascript-obfuscation-1/items?page=1&t=1583981578&sign=d1fc9b35e56b06707f62f6c638c365cc530a694f

  | params | 描述               |
  | :----- | ------------------ |
  | page   | 页数（必选）       |
  | t      | 当前时间戳（可选） |
  | sign   | 签名（必选）       |

  

---

- 查看API的请求调用栈(Requests Call Stack)，依次查看有关的JS代码，即可获得JS的加密代码。

  ![image.png](https://i.loli.net/2020/03/12/KN5Up6QMbrhnGLY.png "image.png")

  ![image.png](https://i.loli.net/2020/03/12/7MzuhvKaLl3fcyr.png "image.png")

  可以看出，sign的生成采用sha1机密，机密对象为( t  - 99 ) / 99，而t的值存储于html中类名为container的p标签的attr属性中

---

- 到此，分析结束，编写代码即可



### 2. 主要代码

- SHA1加密

  ```python
  def hash_encode(t):
      """
      获取加密字符串sign
      原js代码：let sign = sha1('Xr0Z-javascript-obfuscation-1' + t);
      :param t:
      :return:
      """
      str = "Xr0Z-javascript-obfuscation-1" + t
      # sha1加密
      return hashlib.sha1(str.encode("utf-8")).hexdigest()
  ```

  

- Main函数

  ```python
  # url 与 api 映射关系
      url_dicts = {
          "http://www.glidedsky.com/level/web/crawler-javascript-obfuscation-1?page={}".format(i): "http://www.glidedsky.com/api/level/web/crawler-javascript-obfuscation-1/items?page={}".format(i) for i
          in range(1, 1001)
      }
      sum = 0
      for url in url_dicts:
          pre_sum = sum
          print("开始访问 ---> {}".format(url))
          document = do_get(url)  # 访问url
          t = parse_t(document)  # 获取t
          sign = hash_encode(str(t))  # 获取sign
          url_dicts[url] += "&t=" + str(t) + "&sign=" + sign;  # 拼接字符串，获取实际api链接
          print("开始访问 ---> {}".format(url_dicts[url]))
          json_content = do_get(url_dicts[url])  # 访问api
          items = json.loads(json_content)['items']  # 获取所有数字返回值
          for item in items:  # 计算当前页面数字总和
              sum += item
          print("当前页面数字总和为：{}".format(sum - pre_sum))
          print("当数字总和为：{}".format(sum))
  ```




##  总结

​		破解JS反爬逻辑上说比较容易，其核心就在于获取API的加密方式，但因为现在大型的网站的加密流程都非常复杂，因此，在调用栈中一时间难以直接找出实现加密的JS文件，而且**JS反爬涉及的主要是加密算法**，因此，要想进行破解，还必须要知道一些主流的加密方法以及其实现。

## 知识扩展

- SHA1

  > SHA-1是一种数据加密算法，该算法的思想是接收一段明文，然后以一种不可逆的方式将它转换成一段（通常更小）密文，也可以简单的理解为取一串输入码（称为预映射或信息），并把它们转化为长度较短、位数固定的输出序列即散列值（也称为信息摘要或信息认证代码）的过程。

  SHA-1与MD5类似，都是单向操作，具有很强的不可逆性，所以一旦将密码等机密信息嵌入其中，他人只能通过暴力穷举来获得密码，一定程度上，还是比较安全的算法

