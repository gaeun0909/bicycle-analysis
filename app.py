import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정 및 데이터베이스 확인
st.set_page_config(page_title="서울시 따릉이 데이터 분석", layout="wide")

DB_PATH = 'bicycle.db'

def check_db():
    if not os.path.exists(DB_PATH):
        st.error(f"🚨 '{DB_PATH}' 파일을 찾을 수 없습니다! 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요.")
        st.stop()

check_db()

# 데이터베이스 연결 함수
def run_query(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(query, conn)

st.title("🚲 서울시 공공자전거 이용현황 대시보드")
st.markdown("데이터베이스에서 실시간으로 집계한 결과입니다.")

# --- 차트 1: 월별 이용패턴 ---
st.subheader("1. 월별 이용패턴 (Line Chart)")

sql1 = """
SELECT 대여일자, SUM(이용건수) as 총이용건수
FROM 이용정보
GROUP BY 대여일자
ORDER BY 대여일자
"""
df1 = run_query(sql1)

col1_1, col1_2 = st.columns([2, 1])

with col1_1:
    fig1 = px.line(df1, x='대여일자', y='총이용건수', title='월별 따릉이 이용 추이', markers=True)
    st.plotly_chart(fig1, use_container_width=True)

with col1_2:
    st.info("**SQL Query**")
    st.code(sql1, language='sql')
    st.markdown("""
    **💡 인사이트**
    - 날씨가 따뜻해지는 봄/가을에 이용량이 급증하는 경향을 보입니다.
    - 겨울철(12월~2월)에는 추위로 인해 이용 건수가 크게 감소합니다.
    """)

st.divider()

# --- 차트 2: 기온별 평균 이용량 ---
st.subheader("2. 기온별 평균 이용량 (Bar Chart)")

# 기온을 5도 단위로 범주화하여 JOIN
sql2 = """
SELECT 
    (CAST(T.평균기온/5 AS INT) * 5) || '도 ~ ' || (CAST(T.평균기온/5 AS INT) * 5 + 5) || '도' as 기온구간,
    AVG(U.이용건수) as 평균이용건수
FROM 이용정보 U
JOIN 기온 T ON U.대여일자 = T.년월
GROUP BY 기온구간
ORDER BY CAST(T.평균기온/5 AS INT)
"""
df2 = run_query(sql2)

col2_1, col2_2 = st.columns([2, 1])

with col2_1:
    fig2 = px.bar(df2, x='기온구간', y='평균이용건수', color='평균이용건수',
                 title='평균 기온(5도 구간)에 따른 평균 이용건수')
    st.plotly_chart(fig2, use_container_width=True)

with col2_2:
    st.info("**SQL Query**")
    st.code(sql2, language='sql')
    st.markdown("""
    **💡 인사이트**
    - 기온이 20~25도 사이일 때 평균 이용량이 가장 높게 나타납니다.
    - 영하의 기온이나 30도 이상의 혹서기에는 이용률이 눈에 띄게 줄어듭니다.
    """)

st.divider()

# --- 차트 3: 인기 대여소 TOP 10 ---
st.subheader("3. 인기 대여소 TOP 10 (Horizontal Bar Chart)")

sql3 = """
SELECT S.보관소명, SUM(U.이용건수) as 총이용건수
FROM 이용정보 U
JOIN 대여소 S ON U.대여소번호 = S.대여소번호
GROUP BY S.보관소명
ORDER BY 총이용건수 DESC
LIMIT 10
"""
df3 = run_query(sql3).sort_values(by='총이용건수', ascending=True) # 가로 막대는 정렬해주는게 예쁨

col3_1, col3_2 = st.columns([2, 1])

with col3_1:
    fig3 = px.bar(df3, x='총이용건수', y='보관소명', orientation='h', 
                 title='가장 많이 이용하는 대여소 TOP 10',
                 color='총이용건수', color_continuous_scale='Viridis')
    st.plotly_chart(fig3, use_container_width=True)

with col3_2:
    st.info("**SQL Query**")
    st.code(sql3, language='sql')
    st.markdown("""
    **💡 인사이트**
    - 지하철역 인근이나 대규모 공원(여의도, 한강공원 등) 근처 대여소의 이용 비중이 압도적입니다.
    - 출퇴근 및 레저 목적의 수요가 상위권 대여소에 집중되어 있음을 알 수 있습니다.
    """)