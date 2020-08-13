# get-heavens-above

爬取Heavens Above网站，获取国际空间站卫星过境信息，按照星等、太阳高度、持续时间、卫星高度筛选出最适合观测的若干过境事件，获取这些时间的星图和详细信息，并自动生成 `.docx` 格式的天象预报文件。

## 使用方法

首先请确保您的电脑安装了Chrome浏览器。

接着，使用 `pip3` 安装若干依赖：

```
pip3 install bs4
pip3 install selenium
pip3 install python-docx
```

然后，请按照Chrome浏览器的版本在 https://chromedriver.chromium.org/downloads 下载合适的ChromeDriver。Linux 和 MacOS 用户下载好之后, 请将下载好的 `chromedriver` 文件放在你的计算机的 `/usr/bin` 或 `/usr/local/bin`  目录，并赋予执行权限。Windows用户请将下载的文件解压，并将得到的 `chromedriver.exe` 放在系统环境变量的目录下。

最后，执行 `crawl.py` 即可。

```
python ./src/crawl.py
```

## 输出结果

程序会在 `./out/` 目录下生成一个名为 `output.docx` 的文件，内容是筛选出的每次过境的星图和详细信息。而图片保存在 `./out/img/` 目录下。

## 修改配置

修改 `./src/crawl.py` 中第14至19行的常量可以改变经纬度、海拔等配置。修改 `compare()` 函数可以调整排序算法。

## License

Released under the GNU General Public License v3
http://www.gnu.org/licenses/gpl-3.0.html

