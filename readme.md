### XCode Python脚本打包

### 环境
python版本需求: python3
使用前请安装 requirements.text
```shell
pip install -r requirements.text

```

###  配置脚本信息
1. workspace 项目的路径地址
2. project_name 项目名称
3. scheme xcodebuild -list查看
4. display_name显示名 发送钉钉消息时显示名字
5. export_options_plist 导出文件配置使用文件夹中的默认 exportOptions.plist
6. configuration 默认打release还是debug
7. mothod 默认打出包类型 development/ad-hoc/appstore
8. export_path 打包出archive文件导出路径
9. apiKey蒲公英上传api_key
10. dingdingWebHook钉钉机器人发消息地址

### 使用
```shell
查看打包命令
python autoarchive.py -h 
usage: Python脚本打包工具 [-h] [-c Release] [-m ad-hoc]

optional arguments:
  -h, --help            show this help message and exit
  -c Release, --configuration Release
                        该选项用来配置打包配置项类型 可选项：Debug，Release 默认：Release
  -m ad-hoc, --method ad-hoc
                        该选项用来配置打包输出类型 development，ad-hoc，app-store 默认：ad-hoc

python autoarchive.py -c release -m ad-hoc
```

### 其他
打包完成后会在指定的archive路径生产一个projectname名字的文件夹，每次打包通过时间来区分保存，打包的ipa文件在对应的export目录下
