#!/usr/bin/env python
# -*- coding:utf-8 -*-
# -*- author: ChenHao -*-

import argparse
import subprocess
import datetime
import getpass
import os
import plistlib
import upload_pgyer as PgyerUtil
import requests
import json
import time

# 项目目录
workspace_path = '..'
# 导出文件存放地址 这里存放在桌面 可以自定义导出地址
export_root_path = '/Users/%s/Desktop/archiveFile/' % (getpass.getuser())

# 项目名称
project_name = '项目名称'
# 项目scheme   xcodebuild -list  查看   scheme和项目名称不一定一样，所以这里分别配置
scheme = '项目Scheme'
# 显示名字 用于发送钉钉是显示的名字
display_name = '钉钉消息显示的app名称'
# 项目完整路径
workspace = '%s/%s.xcworkspace' % (workspace_path, project_name)
# 导出选项文件
export_options_plist = 'exportOptions.plist'
# 运行模式 debug release
configuration = 'release'
# method development ad-hoc appstore
method = 'ad-hoc'

export_path = '%s%s/%s/' % (export_root_path,
                            project_name, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
archive_path = export_path + project_name
ipa_path = export_path + 'export'

# 蒲公英上传Key
apiKey = '蒲公英APIKey'
# 钉钉webHook
dingdingWebHook = '钉钉机器人webhook地址'
# 清理项目


def clean_project():

    # xcworkspace项目clean
    # ${workspace} 工程中,.xcworkspace的文件名字
    # ${scheme} 当前要编译运行的scheme
    # configuration ${Debug或者Release} 当前是要以Debug运行还是以Release运行
    # -quiet 忽略警告提示打印
    # -UseNewBuildSystem=NO 是否使用新的build系统
    cmd = 'xcodebuild clean -workspace %s -scheme %s -configuration %s' % (
        workspace, scheme, configuration)
    print(cmd)
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
    if process.returncode == 0:
        print('%s.xcworkspace clean success!' % project_name)
    else:
        print('clean 失败')

# 构建项目


def build_project():
    cmd = 'xcodebuild -workspace %s -scheme %s -configuration %s -destination %s build ' % (
        workspace, scheme, configuration,'generic/platform=iOS')
    print(cmd)
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
    if process.returncode == 0:
        print('%s.xcworkspace build success!' % project_name)
    else:
        print('build 失败')

# 打包项目


def archive_project():
    cmd = 'xcodebuild -workspace %s -scheme %s -configuration %s -archivePath %s -destination  %s archive' % (
        workspace, scheme, configuration, archive_path,'generic/platform=iOS')
    print(cmd)
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
    if process.returncode == 0:
        print('archive 成功')
    else:
        print(f'archive失败:{workspace}')

# 导出项目


def export_project():
    archive_file = archive_path + '.xcarchive'
    cmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s -allowProvisioningUpdates" % (
        archive_file, ipa_path, export_options_plist)
    print(cmd)
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
    if process.returncode == 0:
        print('导出archive 成功')
    else:
        print(f'导出archive失败:{workspace}')

# 上传完成回调


def upload_complete_callback(isSuccess, result):
    print(result)
    if isSuccess:
        print('上传完成')
        _data = result['data']
        # 去除首尾空格
        _url = 'https://www.pgyer.com/%s' % _data['buildShortcutUrl'].strip()
        _appVer = _data['buildVersion']
        _buildVer = _data['buildBuildVersion']
        _buildQRCodeURL = _data['buildQRCodeURL']
        _buildCreated = _data['buildCreated']
        print('链接: %s' % _url)
        print('版本: %s (build %s)' % (_appVer, _buildVer))
        send_dingTalk(_url, _buildQRCodeURL, _appVer, _buildCreated)
    else:
        print('上传失败')


# 获取ipa文件
def get_ipafile():
    # 遍历ipa_path文件夹，获取.ipa文件
    file_list = os.listdir(ipa_path)
    for file in file_list:
        if file.endswith('.ipa'):
            cur_path = os.path.join(ipa_path, file)
            return cur_path

# 上传ipa


def upload_ipa():
    ipa_file = get_ipafile()
    # 获取到了ipa文件
    if ipa_file:
        print('获取ipa文件成功：%s' % ipa_file)
        PgyerUtil.upload_to_pgyer(
            path=ipa_file,
            api_key=apiKey,
            callback=upload_complete_callback
        )
    else:
        print('获取ipa文件失败')

def send_dingTalk(url, buildQRCodeURL, appVer, buildCreated):
    data = {
        "msgtype": "markdown",
        "markdown": {
            "text": "### 【%s（iOS）】构建成功\n构建类型：iOS\n构建版本：%s\n[下载地址](%s)\n![](%s)\n构建时间：%s" % (display_name,appVer, url, buildQRCodeURL, buildCreated),
            "title": "【%s（iOS）】构建成功" % display_name,
        },
        'at': {
            "isAtAll": False
        }
    }
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    send_data = json.dumps(data).encode('utf-8')
    print('开始发送钉钉消息...')
    ret = requests.post(url=dingdingWebHook, data=send_data, headers=headers)
    print(ret.text)
    if ret.status_code == requests.codes.ok:
        print('钉钉消息发送成功')
    else:
        print('钉钉消息失败')

def calc_time(run_time):
    hour = run_time//3600
    minute = (run_time-3600*hour)//60
    second = run_time-3600*hour-60*minute
    print (f'构建总时长：{hour}小时{minute}分钟{second}秒')


def xcode_autoarchive():
    begin_time = time.time()
    clean_project()
    # build_project()
    archive_project()
    export_project()
    upload_ipa()
    end_time = time.time()
    calc_time(round(end_time-begin_time))


def prase_args(options):

    # 解析参数
    global configuration
    if options.configuration:
        configuration = options.configuration

    # 读取plist文件
    with open(export_options_plist, 'rb') as fp:
        pl = plistlib.load(fp)
        # 设置method默认值为ad-hoc
        pl['method'] = method

    if options.method:
        # 修改plist文件method内容
        pl['method'] = options.method

    # 写入plist文件
    with open(export_options_plist, 'wb') as fp:
        plistlib.dump(pl, fp)

    # 发起打包
    print('method：%s' % pl)
    print('configuration：%s' % configuration)
    xcode_autoarchive()


if __name__ == "__main__":

    # 1. 定义命令行解析器对象
    parser = argparse.ArgumentParser('Python脚本打包工具')

    # 2. 添加命令行参数
    # configuration Debug Release
    parser.add_argument(
        "-c", "--configuration", help="该选项用来配置打包配置项类型 可选项：Debug，Release 默认：Release",
        metavar="Release")
    # method development, ad-hoc, app-store
    parser.add_argument(
        "-m", "--method", help="该选项用来配置打包输出类型 development，ad-hoc，app-store 默认：ad-hoc",
        metavar="ad-hoc")

    # 3. 从命令行中结构化解析参数
    options = parser.parse_args()
    prase_args(options)
    # print(export_root_path)
