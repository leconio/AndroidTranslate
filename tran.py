#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import hashlib
import time

import requests
import xml.dom.minidom as xmldom
import xml.etree.ElementTree as eTree

DEBUG = False

TO_ANDROID_LANGUAGE = 'your-targe-language'
PROJECT_ROOT_PATH = 'your-project-path'
APPID = "your-appid"
APP_SECRET = "you-appsecret"
FROM_BAIDU_LANGUAGE = 'zh'
TO_BAIDU_LANGUAGE = 'cht'


def pretty_xml(element, indent, newline, level=0):
    if element:
        if element.text is None or element.text.isspace():
            element.text = newline + indent * (level + 1)
        else:
            element.text = newline + indent * \
                (level + 1) + element.text.strip() + \
                newline + indent * (level + 1)
    temp = list(element)
    for subelement in temp:
        if temp.index(subelement) < (len(temp) - 1):
            subelement.tail = newline + indent * (level + 1)
        else:
            subelement.tail = newline + indent * level
        pretty_xml(subelement, indent, newline, level=level + 1)


def tran(q):
    if q is None or q is '':
        return ''
    salt = random.randint(40000, 80000)
    appid = APPID
    secret = APP_SECRET
    m = hashlib.md5()
    sign = ''.join([appid, q, str(salt), secret])
    m.update(sign.encode("utf-8"))
    data = {
        'q': q,
        'from': FROM_BAIDU_LANGUAGE,
        'to': TO_BAIDU_LANGUAGE,
        'appid': appid,
        'salt': salt,
        'sign': m.hexdigest()
    }
    time.sleep(random.randint(1, 100) / 100)
    r = requests.post(
        'https://api.fanyi.baidu.com/api/trans/vip/translate', data)
    return r.json()['trans_result'][0]['dst'] if r.json() is not None else q


def find_multiple_name(output_file):
    mn = []
    if os.path.exists(output_file):
        dom = xmldom.parse(output_file)
        ele = dom.documentElement
        for node in ele.getElementsByTagName("string"):
            name = node.getAttribute('name')
            mn.append({
                "name": name,
                "text": node.firstChild.data if hasattr(node.firstChild, 'data') else ''
            })
    return mn


def find_origin_str(file, output_file):
    print("翻译中%s" % file)
    dom = xmldom.parse(file)
    ele = dom.documentElement
    root = eTree.Element("resources")

    mn = find_multiple_name(output_file)

    for node in ele.getElementsByTagName("string"):
        name = node.getAttribute('name')
        value = node.firstChild.data if hasattr(
            node.firstChild, 'data') else ''
        string_node = eTree.SubElement(root, 'string', {'name': name})
        the_text = None
        for m in mn:
            if name in m["name"]:
                the_text = m['text']
                break
        if the_text:
            string_node.text = the_text
        else:
            string_node.text = tran(value.replace(
                '\\', '//-//')).replace('//-//', '\\')
            print("在线翻译：:%s，翻译结果:%s" % (value, string_node.text))

    pretty_xml(root, '    ', '\n')
    tree = eTree.ElementTree(root)
    tree.write(output_file, "utf-8")


def search(path, name):
    rf = []
    for root, dirs, files in os.walk(path, topdown=False):  # path 为根目录
        if name in files and 'values' in root and '-' not in root:
            rf.append(os.path.join(root, name))

    return rf


if __name__ == '__main__':
    print('Start...')
    print("执行路径：" + PROJECT_ROOT_PATH)
    for origin_path in search(PROJECT_ROOT_PATH, "strings.xml"):
        # 创建文件夹
        root_path = os.path.dirname(os.path.dirname(origin_path))

        if TO_ANDROID_LANGUAGE not in os.listdir(root_path):
            os.mkdir(os.path.join(root_path, TO_ANDROID_LANGUAGE))
            break
        try:
            find_origin_str(origin_path, os.path.join(
                os.path.join(root_path, TO_ANDROID_LANGUAGE), "strings.xml"))
        except Exception as e:
            print(e)
    print('End...')
