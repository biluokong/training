import re

import streamlit as st
import streamlit_echarts

from utils import util
from utils.util import ChartsType

# 配置当前网页的基本信息
st.set_page_config(page_title='网站关键词出现频率）', page_icon='🐛', layout='wide')
# 设置侧边栏的内容
st.sidebar.header('网站关键词出现频率')
selected_type = st.sidebar.selectbox('您希望以哪种图显示：', (
    ChartsType.Bar.value,
    ChartsType.Line.value,
    ChartsType.Pie.value,
    ChartsType.WordCloud.value,
    ChartsType.Scatter.value,
    ChartsType.Funnel.value,
    ChartsType.TreeMap.value,
    ChartsType.PictorialBar.value
)
                                     )
st.markdown('# 统计网站内容的词频')
# 添加文字输入框
url = st.text_input('请输入你想爬取的网站的url')

if st.button('查询'):
    if not re.search(util.URL_REG, url):
        st.markdown(':red[请输入正确的网址！]')

    else:
        try:
            # 获取指定url里指定标签的所有内容
            items, content = util.get_html_content(url)
            if not content:
                st.markdown('# :red[爬取失败，请输入其他url！]')
            else:
                # 根据获取的网页文本数据创建图表
                myChart = util.draw_words_counter(content, ChartsType(selected_type))
                streamlit_echarts.st_pyecharts(myChart,
                                               height='800px'
                                               if ChartsType(selected_type) in [ChartsType.Pie, ChartsType.Funnel]
                                               else '400px')
        except OSError as e:
            st.markdown(':red[请输入存在的网址！]')
