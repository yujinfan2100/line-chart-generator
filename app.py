import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
import os

# 设置页面配置
st.set_page_config(
    page_title="📊 折线图生成器",
    page_icon="📈",
    layout="wide"
)

# 设置中文字体
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

# 标题
st.markdown("""
    <h1 style='text-align: center; color: #2E86C1;'>
        📊 折线图生成器 Pro
    </h1>
    <p style='text-align: center; color: #566573;'>
        支持CSV、Excel、TXT文件，可直接粘贴数据
    </p>
    <hr>
""", unsafe_allow_html=True)

# 初始化session state
if 'x_data' not in st.session_state:
    st.session_state.x_data = []
if 'y_data' not in st.session_state:
    st.session_state.y_data = []

# 侧边栏 - 数据源选择
st.sidebar.markdown("## 📁 1. 选择数据源")
data_source = st.sidebar.radio(
    "数据源类型",
    ['📋 示例数据', '📝 手动输入', '🎲 随机生成', '📁 上传文件', '📋 粘贴数据'],
    index=0
)

# 主界面分两列
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("## 📊 2. 数据设置")

    # ============ 示例数据 ============
    if data_source == '📋 示例数据':
        st.info("使用内置示例数据")
        x_data = [1, 2, 3, 4, 5, 6, 7]
        y_data = [23, 45, 56, 78, 65, 89, 92]

        df_demo = pd.DataFrame({
            'X轴': x_data,
            'Y轴': y_data
        })
        st.dataframe(df_demo, use_container_width=True)

        st.session_state.x_data = x_data
        st.session_state.y_data = y_data

    # ============ 手动输入 ============
    elif data_source == '📝 手动输入':
        st.info("请输入数据（用逗号分隔）")

        x_input = st.text_input(
            "X轴数据",
            value="1,2,3,4,5,6,7",
            help="例如：1,2,3,4,5,6,7"
        )

        y_input = st.text_input(
            "Y轴数据",
            value="23,45,56,78,65,89,92",
            help="例如：23,45,56,78,65,89,92"
        )

        try:
            x_data = [float(i.strip()) for i in x_input.split(',')]
            y_data = [float(i.strip()) for i in y_input.split(',')]

            if len(x_data) == len(y_data):
                st.session_state.x_data = x_data
                st.session_state.y_data = y_data

                df_manual = pd.DataFrame({
                    'X轴': x_data,
                    'Y轴': y_data
                })
                st.dataframe(df_manual, use_container_width=True)
            else:
                st.error("❌ X轴和Y轴数据长度不一致！")
        except:
            st.error("❌ 数据格式错误！请使用逗号分隔的数字")

    # ============ 随机生成 ============
    elif data_source == '🎲 随机生成':
        st.info("随机生成数据")

        col_n, col_min, col_max = st.columns(3)
        with col_n:
            n_points = st.number_input("数据点数", min_value=3, max_value=50, value=10)
        with col_min:
            min_val = st.number_input("最小值", value=10)
        with col_max:
            max_val = st.number_input("最大值", value=90)

        if st.button("🎲 重新生成"):
            np.random.seed(42)
            x_data = list(range(1, n_points + 1))
            y_data = list(np.random.randint(min_val, max_val + 1, n_points))

            st.session_state.x_data = x_data
            st.session_state.y_data = y_data

            df_random = pd.DataFrame({
                'X轴': x_data,
                'Y轴': y_data
            })
            st.dataframe(df_random, use_container_width=True)

    # ============ 上传文件 ============
    elif data_source == '📁 上传文件':
        st.info("上传数据文件")

        uploaded_file = st.file_uploader(
            "选择文件",
            type=['csv', 'xlsx', 'xls', 'txt'],
            help="支持CSV、Excel、TXT格式"
        )

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file)
                else:
                    df = pd.read_csv(uploaded_file, sep=None, engine='python')

                st.success(f"✅ 成功读取文件：{uploaded_file.name}")
                st.write("数据预览：")
                st.dataframe(df.head(10), use_container_width=True)

                columns = df.columns.tolist()

                col_x = st.selectbox("选择X轴列", columns, index=0)
                col_y = st.selectbox("选择Y轴列", columns, index=min(1, len(columns)-1))

                if st.button("📥 导入数据", type="primary"):
                    st.session_state.x_data = df[col_x].tolist()
                    st.session_state.y_data = df[col_y].tolist()
                    st.success(f"✅ 成功导入 {len(st.session_state.x_data)} 个数据点")

            except Exception as e:
                st.error(f"❌ 读取失败：{e}")

    # ============ 粘贴数据 ============
    elif data_source == '📋 粘贴数据':
        st.info("从Excel复制数据后粘贴")

        paste_data = st.text_area(
            "粘贴区域",
            height=150,
            placeholder="示例：\n1,23\n2,45\n3,56\n4,78",
            help="第一列是X轴，第二列是Y轴，用逗号或制表符分隔"
        )

        if paste_data:
            try:
                from io import StringIO
                df = pd.read_csv(StringIO(paste_data), sep=None, engine='python')

                st.write("数据预览：")
                st.dataframe(df.head(10), use_container_width=True)

                columns = df.columns.tolist()
                col_x = st.selectbox("X轴列", columns, index=0, key='paste_x')
                col_y = st.selectbox("Y轴列", columns, index=min(1, len(columns)-1), key='paste_y')

                if st.button("📥 导入粘贴数据", type="primary"):
                    st.session_state.x_data = df[col_x].tolist()
                    st.session_state.y_data = df[col_y].tolist()
                    st.success(f"✅ 成功导入 {len(st.session_state.x_data)} 个数据点")

            except Exception as e:
                st.error(f"❌ 解析失败：{e}")

    # ============ 图表样式设置 ============
    st.markdown("---")
    st.markdown("## 🎨 3. 图表样式")

    chart_title = st.text_input("图表标题", "我的折线图")
    x_label = st.text_input("X轴标签", "X轴")
    y_label = st.text_input("Y轴标签", "Y轴")

    col_color, col_marker = st.columns(2)
    with col_color:
        line_color = st.selectbox(
            "线条颜色",
            ['blue', 'red', 'green', 'orange', 'purple', 'black'],
            index=0
        )
    with col_marker:
        marker_style = st.selectbox(
            "标记样式",
            ['o', 's', '^', 'D', '*', '+', 'x'],
            index=0
        )

    col_width, col_size = st.columns(2)
    with col_width:
        line_width = st.slider("线宽", 0.5, 5.0, 2.0, 0.5)
    with col_size:
        marker_size = st.slider("标记大小", 4, 20, 8)

    col_grid, col_values = st.columns(2)
    with col_grid:
        show_grid = st.checkbox("显示网格", True)
    with col_values:
        show_values = st.checkbox("显示数值", True)

# ============ 图表显示 ============
with col2:
    st.markdown("## 📈 4. 生成的图表")

    if st.session_state.x_data and st.session_state.y_data:
        x_data = st.session_state.x_data
        y_data = st.session_state.y_data

        if len(x_data) == len(y_data):
            fig, ax = plt.subplots(figsize=(10, 6))

            ax.plot(x_data, y_data,
                   marker=marker_style,
                   markersize=marker_size,
                   linewidth=line_width,
                   color=line_color,
                   label='数据系列')

            if show_values:
                y_max = max(y_data)
                y_min = min(y_data)
                offset = (y_max - y_min) * 0.05 if y_max != y_min else 1

                for i in range(len(x_data)):
                    ax.text(x_data[i], y_data[i] + offset,
                           f'{y_data[i]}',
                           ha='center', va='bottom',
                           fontsize=9,
                           bbox=dict(boxstyle='round,pad=0.3', 
                                   facecolor='yellow', alpha=0.7))

            ax.set_title(chart_title, fontsize=16, fontweight='bold')
            ax.set_xlabel(x_label, fontsize=12)
            ax.set_ylabel(y_label, fontsize=12)

            x_min, x_max = min(x_data), max(x_data)
            y_min, y_max = min(y_data), max(y_data)
            x_range = x_max - x_min if x_max != x_min else 1
            y_range = y_max - y_min if y_max != y_min else 1

            ax.set_xlim(x_min - x_range * 0.1, x_max + x_range * 0.1)
            ax.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.1)

            if show_grid:
                ax.grid(True, linestyle='--', alpha=0.3)

            ax.legend(loc='best')

            st.pyplot(fig)
            plt.close()

            st.markdown("---")
            st.markdown("### 📊 数据统计")

            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("数据点数", len(x_data))
                st.metric("X轴范围", f"{min(x_data):.1f} - {max(x_data):.1f}")
            with col_stat2:
                st.metric("Y轴平均值", f"{np.mean(y_data):.2f}")
                st.metric("Y轴中位数", f"{np.median(y_data):.2f}")
            with col_stat3:
                st.metric("Y轴最大值", max(y_data))
                st.metric("Y轴最小值", min(y_data))

            if len(y_data) > 1:
                trend = '📈 上升' if y_data[-1] > y_data[0] else '📉 下降'
                change = ((y_data[-1] - y_data[0]) / y_data[0]) * 100
                st.info(f"**整体趋势：** {trend} {abs(change):.1f}%")

            df_export = pd.DataFrame({
                'X轴': x_data,
                'Y轴': y_data
            })

            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 下载数据",
                data=csv,
                file_name="chart_data.csv",
                mime="text/csv"
            )

        else:
            st.error("❌ X轴和Y轴数据长度不一致！")
    else:
        st.info("👈 请在左侧设置数据")

st.markdown("---")
st.markdown("""
    <p style='text-align: center; color: #888;'>
        ✨ 支持CSV、Excel、TXT文件，可直接复制Excel数据粘贴<br>
        有问题？请联系管理员
    </p>
""", unsafe_allow_html=True)
