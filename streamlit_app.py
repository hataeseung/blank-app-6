import streamlit as st
import pandas as pd
import altair as alt

# 타이틀과 안내 메시지
st.title("🎈 통합국사 DUH_SFP 고온 Report ")

# 문구들을 중앙 정렬로 표시
st.markdown(
    """
    <div style='text-align: center;'>
        업로드된 데이터를 기반으로 통합국사별 60˚C 이상 고온 DUH_SFP 현황을 보여줍니다.
    </div>
    """, 
    unsafe_allow_html=True
)

# 이모지를 건물 오른쪽에 온도계가 있도록 배치
st.markdown(
    """
    <div style='text-align: center; color: red;'>
        통합국사 담당자께서는 조치 부탁드립니다.
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style='display: flex; justify-content: center; align-items: center;'>
        <span style='font-size: 80px;'>🏢</span>
        <span style='font-size: 80px; margin-left: 10px;'>🌡️</span>
    </div>
    """,
    unsafe_allow_html=True
)

# 파일 업로드 위젯
st.markdown("<b style='color: blue;'>CSV 파일을 업로드하세요</b>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type="csv")

if uploaded_file is not None:
    # CSV 파일을 판다스로 읽음
    df = pd.read_csv(uploaded_file)
    
    # dt 열을 문자열로 변환한 후, 날짜 형식으로 변환하고 시분초 제거
    if 'dt' in df.columns:
        df['dt'] = df['dt'].astype(str)
        df['dt'] = pd.to_datetime(df['dt'], format='%Y%m%d', errors='coerce').dt.strftime('%Y-%m-%d')

    # temp1 열을 숫자로 변환 (NaN 값은 0으로 처리하고 소수점 제거)
    df['temp1'] = pd.to_numeric(df['temp1'], errors='coerce').fillna(0).astype(int)  # NaN을 0으로 대체한 후 정수 변환

    # temp1이 60 이상인 행의 수를 카운트하여 리포트 생성
    if 'region' in df.columns and 'site_name' in df.columns and 'temp1' in df.columns:
        report_df = df[df['temp1'] >= 60].groupby(['region', 'site_name']).size().reset_index(name="high temp(60˚C 이상)")

        # high temp(60˚C 이상) 열의 값이 1 이상인 경우만 필터링
        report_df = report_df[report_df["high temp(60˚C 이상)"] >= 1]
        
        # 열 이름을 사용자가 지정한 대로 수정
        report_df.rename(columns={
            'region': '지역',
            'site_name': '국사명',
            'high temp(60˚C 이상)': '고온(60˚C 이상) SFP 수량'
        }, inplace=True)

        # 리포트 출력 (굵은 글씨체로 변경)
        st.markdown("**📝 통합국사별 DUH_SFP 고온 수량 Report (60˚C 이상인 SFP가 1개 이상인 경우) :**")

        # 중앙 정렬 CSS 스타일을 적용하여 HTML로 테이블 생성
        styled_table = report_df.to_html(index=False)
        styled_table = f"""
        <style>
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ text-align: center; font-weight: bold; }}
            td {{ text-align: center; }}
        </style>
        {styled_table}
        """
        st.write(styled_table, unsafe_allow_html=True)

        # Altair 그래프 생성 (short_name 표시, 전체 이름은 툴팁으로 표시)
        report_df['short_name'] = report_df['국사명'].apply(lambda x: '-'.join(x.split('-')[:2]))
        chart = alt.Chart(report_df).mark_bar().encode(
            x=alt.X('short_name:N', title='Site Name (Short)', axis=alt.Axis(labelAngle=-45, tickMinStep=1, labelOverlap=False)),
            y=alt.Y('고온(60˚C 이상) SFP 수량:Q', title='High Temp (60˚C 이상) 수량'),
            tooltip=['국사명', '고온(60˚C 이상) SFP 수량']
        ).properties(
            title="📊 통합국사별 DUH_SFP 고온 수량 (그래프)" 
        ).configure_axis(labelFontSize=12)
        
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("region, site_name, 또는 temp1 열을 찾을 수 없습니다.")
