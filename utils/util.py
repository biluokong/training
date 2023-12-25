import re
from collections import Counter
from enum import Enum
from typing import Pattern, Tuple, List

import jieba
import requests
from bs4 import BeautifulSoup
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, WordCloud, Scatter, Funnel, TreeMap, PictorialBar
from pyecharts.charts.chart import RectChart

URL_REG = r'http(s)?://([a-z0-9-]+.)+[a-z0-9-]{2,}(/?.*)?'


class ChartsType(Enum):
    Bar = '柱状图'
    Line = '线形图'
    Pie = '饼状图'
    WordCloud = '词云图'
    Scatter = '散点图'
    Funnel = '漏斗图'
    TreeMap = '矩形树图'
    PictorialBar = '象形柱图'


def html_filter(text: str, pattern: Pattern = None) -> str:
    """
    过滤出中文

    :param text: 需要过滤的字符串
    :param pattern:  匹配其它需要删除的字符
    """

    # 使用正则表达式去除HTML标签
    # text = re.sub('<[^>]+>', '', text)

    # 过滤出中文
    text = re.sub(r'[^\u4e00-\u9fa5]', '', text)

    # 去除其它需要删除的字符
    if pattern is not None:
        text = re.sub(pattern, '', text)

    return text


def text_participle(text: str) -> list:
    """
    进行中英文分词（并去掉单字符）
    """

    # 使用jieba进行中文分词（去掉中英文单字符）
    words = [i for i in jieba.lcut(text) if len(i) != 1]

    return words


def statistical_word(words: list, count: int = None) -> List[Tuple[str, int]]:
    """
    统计每个不同词的个数，并进行词频排序，返回前count个

    :param words: 要统计的词的列表
    :param count: 要返回前多少名
    """

    # 统计词频
    word_counts = Counter(words)

    # 获得词频最高的count个词
    top_words = word_counts.most_common(count)

    return top_words


def get_words_counts(text: str, pattern: Pattern = None, count: int = None) -> Tuple[List[Tuple], List[str], List[int]]:
    """
    提取出文本中的中文内容，对其进行分词，并去掉单字词，获得词频前count名的元组，元组元素为：[[tuples], words, counts]

    :param text: 文本
    :param pattern: 要过滤掉的其它中文字符的匹配模式
    :param count: 取词频排序后的前多少名，None为全部
    """

    # 过滤出中文字符
    text = html_filter(text, pattern)
    # 对文本内容进行分词，返回分词的列表
    words = text_participle(text)
    # 统计词频
    words_counts = statistical_word(words, count)

    return words_counts, [key for key, _ in words_counts], [value for _, value in words_counts]


def get_html_content(url: str, tags: List[str] = None, joinStr: str = '') -> Tuple[list, str]:
    """
    根据url获取指定网页所有指定tag标签里的内容

    :param url: 网页地址
    :param tags: 标签名列表，默认值['div']
    :param joinStr: 每个标签里的内容拼接时指定的分隔符
    :return: Tuple[list: ResultSet, str]
    """

    # 发送GET请并获取响应
    response = requests.get(url)

    # 根据文本的内容来推测它的编码方式，防止中文乱码输出。
    response.encoding = response.apparent_encoding

    # 使用BeautifulSoup解析响应文本
    soup = BeautifulSoup(response.content, 'html.parser')

    # 获取网页中所有指定标签的内容
    items = []
    if tags is None:
        tags = ['div']
    for tag in tags:
        items += soup.find_all(tag)
    content = joinStr.join([i.text for i in items])

    return items, content


def set_coordinate(chart: RectChart, words: List[str], counts: List[int]):
    # x坐标
    chart.add_xaxis(words)
    # y坐标
    chart.add_yaxis("词频", counts)
    # 让字变斜45度显示，以便让元素尽可能可以显示出来
    chart.set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)))
    # 互换x、y轴
    # bar_chart.reversal_axis()


def draw_words_counter(text: str, chart_type: ChartsType = ChartsType.Bar, count: int = 20,
                       title: str = '') -> RectChart:
    """
    根据指定的文本内容生成指定类型的词频统计图表

    :param text: 文本内容
    :param chart_type: 图表类型
    :param count: 取词频前多少个词
    :param title: 图表的标题
    """

    # 提取出文本内容的中文内容，并进行分词统计
    words_counts, words, counts = get_words_counts(text, count=count)
    # 设置图表的宽高
    chart = None
    if chart_type == ChartsType.Bar:
        chart = Bar()
        set_coordinate(chart, words, counts)
    elif chart_type == ChartsType.Line:
        chart = Line()
        set_coordinate(chart, words, counts)
    elif chart_type == ChartsType.Scatter:
        chart = Scatter()
        set_coordinate(chart, words, counts)
    elif chart_type == ChartsType.Pie:
        chart = Pie()
        chart.add('词频统计', words_counts)
    elif chart_type == ChartsType.WordCloud:
        chart = WordCloud()
        # shape：词云图轮廓
        chart.add('词频统计', words_counts, word_size_range=[20, 80], shape='star')
    elif chart_type == ChartsType.Funnel:
        chart = Funnel()
        chart.add('词频统计', words_counts, itemstyle_opts=opts.ItemStyleOpts())
    elif chart_type == ChartsType.TreeMap:
        chart = TreeMap()
        chart.add('词频统计', [{'value': v, 'name': k} for k, v in words_counts], )
    elif chart_type == ChartsType.PictorialBar:
        chart = PictorialBar(opts.InitOpts())
        set_coordinate(chart, words, counts)

    # 设置图表的标题
    # chart.set_global_opts(title_opts=opts.TitleOpts(title=title))
    # 把图表生成html文件
    # bar.render("word_frequency.html")
    return chart
