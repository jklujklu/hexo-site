---
title: GlidedSky 爬虫挑战-CSS反爬-1
date: 2020-6-1 18:38:45
categories: 
    - 爬虫
tags: 
    - Python
    - GlidedSky
mp3: http://m7.music.126.net/20200615162801/a906800a4eff3d0e0efc1123b4973313/ymusic/870b/ad32/3709/aef735503eb694409ad48e3312f3e752.mp3
cover: http://api.mtyqx.cn/tapi/random.php
---
# GlidedSky 爬虫挑战-CSS反爬-1

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

  [http://glidedsky.com/level/web/crawler-css-puzzle-1](http://glidedsky.com/level/web/crawler-css-puzzle-1)

  > CSS可以排版出精美的页面；CSS也可以通过各种操作，使得用户最终看到的内容和HTML源码的内容千差万别。
  >
  > 此种反爬方式，只需要找到每个元素的标签，并分析其对应的style，即可获得数据
  
  ---
  
- 查看网页源代码，可以看出所有的数字顺序已经被打乱，且存在多余的数字进行干扰

  ![image.png](https://i.loli.net/2020/03/12/yNZSoqatEOP6Lwm.png "image.png")

  ---

  ![image.png](https://i.loli.net/2020/03/12/ZQiLTnNH34jx61B.png "image.png")

  ---

- 进一步读取标签的style，可以看出每个数字均采用float方式，而其显示的位置依赖于left属性

---

- 采取浮动显示的元素，会默认按顺序（本网站中采取从左往右）依次进行排列，如果有额外的left属性，只需要将其左移相对的位置即可

---

- 到此，分析结束，编写代码即可



### 2. 主要代码

- 主函数

  ```python
  def css_start(self):
          """
          GlidedSky CSS反爬
          设计思路：
              1. 根据网站构造1000条url，及其对应的api地址
              2. 获取所有符合条件的div
              3. 根据div的class属性，获取每个div的style，其中style的判断分为以下几种
                  - 具有opacity属性，即该div应该被隐藏
                  - 具有:before属性，此时该div显示的数字隐藏在content中，直接获取即可
                  - 以上都不具备，则根据left属性来判断当前div应该显示的位置
          """
          urls = self.urls.css_get_urls()  # 获取所有url
          sum = 0
          for url in urls:
              sum_current = 0
              print("开始爬取 ---> {}".format(url))
              document = self.download.do_get(url, headers=headers)  # 获取网页响应
              self.parse.set_document(document)  # 向数据解析模块传入document
              classes = self.parse.css_parse_div_class()  # 获取所有符合条件的div
              for cs in classes:
                  num_str = ""  # div拼接出的数字
                  num_offset = {}  # div位置与内容的映射
                  left = 0  # div不考虑偏移时应该在的位置
                  for key in cs.keys():
                      styles = self.parse.css_parse_style(key)  # 获取该div所有style
                      if 'opacity' in styles:  # 要隐藏的div
                          continue
                      elif 'content' in styles:  # 有:before属性的div
                          num_str = styles['content'].replace('"', '').strip(" ")
                          break
                      else:  # 需要计算偏移的div
                          if 'left' not in styles:  # 没有偏移量，即偏移为0
                              offset = 0
                              step = left + offset
                          else:
                              offset = eval(styles['left'].replace("em", ""))  # 获取偏移
                              step = left + offset
                          num_offset.update({step: cs.get(key)})  # 将div实际位置与div的内容形成字典
                          left += 1  # 下一个div的默认位置需要 +1
                  if len(num_offset) > 0:  # 位置的映射关系存在，将其，按key（位置）的值进行排序
                      num_offset = sorted(num_offset.items(), key=lambda d: d[0])
                      for item in num_offset:  # 拼接数字，形成最终结果
                          num_str += item[1]
                  if len(num_str) > 0:
                      sum_current += eval(num_str)  # 数字相加，最终形成当前url中的数字总和
                      print(num_str)
                  print("--------------")
  
              sum += sum_current
              print("\t当前页面数字总和：{}".format(sum_current))
              print("\t当前总和位：{}".format(sum))
          print("总和位：{}".format(sum))
  ```

  

- 获取某个div所有的styles

  ```python
  def css_parse_style(self, class_name):
      if self.document is None:
          print("请先传入要解析的Document！")
          return None
      pattern = re.compile('\.' + class_name + '.*\s?{\s?(.+):(.+)\s?}')
      matches = pattern.findall(self.document)
      result_set = {}
      for match in matches:
          result_set.update({match[0]: match[1]})
      return result_set
  ```

  




##  总结

​		css反爬考验的主要是对前端内容是否熟悉，只要针对数据的布局进行分析，找出其显示数据的规律，即可破解CSS类型的反爬





