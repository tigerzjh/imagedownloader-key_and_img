""" Download image according to given urls and automatically rename them in order. """
# -*- coding: utf-8 -*-
from __future__ import print_function

import shutil
import imghdr
import os
import concurrent.futures
import requests

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Proxy-Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, sdch",
    # 'Connection': 'close',
}


def download_image(image_url, dst_dir, file_name, timeout=20, proxy_type=None, proxy=None):
    proxies = None
    if proxy_type is not None:
        proxies = {
            "http": proxy_type + "://" + proxy,
            "https": proxy_type + "://" + proxy
        }

    response = None
    file_path = os.path.join(dst_dir, file_name) #图片绝对地址 #'./download_images\\Google_0015'
    try_times = 0
    while True:
        try:
            try_times += 1
            response = requests.get(
                image_url, headers=headers, timeout=timeout, proxies=proxies) #访问界面
            with open(file_path, 'wb') as f: #以二进制文本写入
                f.write(response.content) #到末尾自动关闭文件
            response.close()
            file_type = imghdr.what(file_path) #'jpeg'
            # if file_type is not None:
            if file_type in ["jpg", "jpeg", "png", "bmp"]:
                new_file_name = "{}.{}".format(file_name, file_type) #'Google_0015.jpeg'
                new_file_path = os.path.join(dst_dir, new_file_name)#'./download_images\\Google_0015.jpeg'
                shutil.move(file_path, new_file_path) #本来都是空白的图 一过这个语句 图就出来了 太tm神奇了 #(oldfile,newfile)
                print("## OK:  {}  {}".format(new_file_name, image_url))
            else:
                os.remove(file_path)
                print("## Err:  {}".format(image_url))
            break
        except Exception as e:
            if try_times < 3:
                continue
            if response:
                response.close()
            print("## Fail:  {}  {}".format(image_url, e.args))
            break


def download_images(image_urls, dst_dir, file_prefix="img", concurrency=50, timeout=20,proxy_type=None, proxy=None):
    """
    Download image according to given urls and automatically rename them in order.
    :param timeout: 20
    :param proxy: none
    :param proxy_type: none
    :param image_urls: list of image urls
    :param dst_dir: output the downloaded images to dst_dir
    :param file_prefix: if set to "img", files will be in format "img_xxx.jpg"
    :param concurrency: number of requests process simultaneously  同时请求数50
    :return: none
    """

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor: #使用线程池进行
        future_list = list()
        count = 0
       # dst_dir += "/" + keyword
        if not os.path.exists(dst_dir): #没有输出文件夹先创建一个
            os.makedirs(dst_dir)
        for image_url in image_urls: #循环在这里
            file_name = file_prefix + "_" + "%04d" % count #“_0001” 文件名
            future_list.append(executor.submit(
                download_image, image_url, dst_dir, file_name, timeout, proxy_type, proxy))
            #给download_image函数传入 image_url,地址，  google_0000，20，      none,     none
            count += 1
        concurrent.futures.wait(future_list, timeout=180)
