---
title: LazyLoad，图片预加载
date: 2020-6-4 18:38:45
categories: 
    - 教程
tags: 
    - JavaScript
---
# LazyLoad（预加载）

> html默认会加载页面中所有的img标签，而当一个页面拥有很多的图片时，其图片加载的默认机制就会极大的降低用户的使用体验，因为每张图片的加载都需要建立一次Http请求，而这种请求是非常消耗时间的，而且很多图片的加载并没有必要，因为这些图片并不在用户的可视范围中。


## 1. 相关参数

![](https://upload-images.jianshu.io/upload_images/8562733-efdb3b076238ebd1.png?imageMogr2/auto-orient/strip|imageView2/2/w/700/format/webp)

- 视窗大小（innerHeight）

  ```javascript
  var innerHeight = window.innerHeight;
  ```

- 已滚动过的距离（scrollTop）

  ```javascript
  let scrollTop = document.documentElement.scrollTop;
  ```

- 元素与页面顶部的距离（offsetTop）

  ```javascript
  let itemOffsetTop = items[i].offsetTop;
  ```

## 2. 实现方法

1. 对scroll事件进行监听
2. 遍历需要预加载的对象，判断其是否需要加载，判断根据：offsetTop <  ( scrollTop + innerHeight) 
3. 将img标签的data-src属性赋值给src，实现加载

## 3. 代码实现

```javascript
function lazyload(scrollTop){
    // 内部for循环执行次数
    let count = 0;
    // 遍历所有元素
    for (let i=index;i<items.length;i++){
        // 获取当前元素的img标签
        let img = items[i].querySelector('img')
        // 获取当前元素顶部与HTML顶部的距离
        let itemOffsetTop = items[i].offsetTop;
        // 当（元素与顶部距离）小于（页面滚动过的距离与视窗高度的和）时，说明当前元素已处于可视范围
        // 此时将其显示
        if (itemOffsetTop <= innerHeight + scrollTop){
            // 如果其src属性不为空，说明此元素之前已被加载过，跳过此元素
            if (img.getAttribute('src') != ""){
                continue
            // 否则，更新src属性，加载图片
            }else{
                img.setAttribute('src',img.getAttribute('data-src'));
                // 更新下一个需要预加载的索引
                index = i;
            }
        }
        count += 1;
    }
    console.log(count);
}
```

## 4. 优化

### 1. onScroll优化

####  简述

onscroll的触发频率非常快，其频率大概在20ms左右，如果不加以优化，会导致lazyload函数被频繁调用，影响性能

#### 方法

设定一个等待变量，只有处于非等待状态时，lazyload才被触发。而一旦函数被调用，立即将变量置为等待状态，并设立一个延时，自动的重置变量，使其变为非等待状态。

```javascript
// 监听滚动，当屏幕进行滚动时触发
window.onscroll = function(){
    // 处于等待状态，直接退出
    if (waiting){
        return
    }
    // 否则，将其改变为等待状态
    waiting = true;
    // 获取已经滚动过的高度
    let scrollTop = document.documentElement.scrollTop;
    // 执行预加载
    lazyload(scrollTop);
    // 设置延时，0.1s后自动释放资源
    setTimeout(function(){
        waiting = false;
    },100);
}
```

## 5. 项目地址

[Codepen](https://codepen.io/jklujklu/pen/jObBXNj)

