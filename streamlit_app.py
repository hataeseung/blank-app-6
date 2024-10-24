import streamlit as st
import pandas as pd
import altair as alt

# 타이틀과 안내 메시지
st.title("🎈 통합국사 DUH_SFP 고온 Report ")

# 문구들을 중앙 정렬로 표시
st.markdown(
    """
    <div style='text-align: center;'>
        업로드된 데이터를 기반으로 통합국사별 60˚C 이상 고온 DUH_SFP 수량을 보여줍니다.
    </div>
    """, 
    unsafe_allow_html=True
)

# 이모지를 건물 오른쪽에 온도계가 있도록 배치
st.markdown(
    """
    <div style='text-align: center; color: red;'>
        통합국사 담당자께서는 사전조치 부탁드립니다.
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

    # 데이터의 처음 5줄을 미리보기 (dt 열 형식 적용)
    st.write("📊 업로드 데이터 미리보기 :")
    st.write(df.head())

    # temp1이 60 이상인 행의 수를 카운트하여 리포트 생성
    if 'region' in df.columns and 'site_name' in df.columns and 'temp1' in df.columns and 'duh_name' in df.columns:
        report_df = df[df['temp1'] >= 60].groupby(['region', 'site_name', 'duh_name']).size().reset_index(name="high temp(60˚C 이상)")

        # high temp(60˚C 이상) 열의 값이 2 이상인 경우만 필터링
        report_df = report_df[report_df["high temp(60˚C 이상)"] >= 2]
        
        # 리포트 출력
        st.write("📊 통합국사별 DUH_SFP 고온 수량 Report (60˚C 이상인 SFP가 2개 이상인 경우) :")
        st.write(report_df)

        # site_name을 요약하여 더 짧은 형태로 표시 (예: '서울-01'처럼 '-' 앞의 두 단어로 축약)
        report_df['short_name'] = report_df['site_name'].apply(lambda x: '-'.join(x.split('-')[:2]))

        # Altair 그래프 생성 (short_name 표시, 전체 이름은 툴팁으로 표시)
        chart = alt.Chart(report_df).mark_bar().encode(
            x=alt.X('short_name:N', title='Site Name (Short)', axis=alt.Axis(labelAngle=-45, tickMinStep=1, labelOverlap=False)),  # 레이블 회전 및 겹침 방지
            y=alt.Y('high temp(60˚C 이상):Q', title='High Temp (60˚C 이상) 수량'),
            tooltip=['site_name', 'high temp(60˚C 이상)']  # 마우스를 올리면 전체 이름 표시
        ).properties(
            title="통합국사별 DUH_SFP 고온 수량"
        ).configure_axis(
            labelFontSize=12  # 축 레이블 크기 설정
        )

        st.altair_chart(chart, use_container_width=True)

        # site_name 선택
        st.markdown("<b style='color: blue;'>고온 상세현황을 알고 싶으면 통합국사명(site_name)을 선택하세요</b>", unsafe_allow_html=True)
        selected_site = st.selectbox("", report_df['site_name'].unique())
        
        # 선택한 site_name에 해당하는 행을 출력
        if selected_site:
            filtered_df = df[(df['site_name'] == selected_site) & (df['temp1'] >= 60)]
            
            # 테이블 크기 및 열 중앙 정렬을 위한 스타일 적용
            styled_df = filtered_df.style.set_table_styles(
                [{'selector': 'th', 'props': [('text-align', 'center')]},  # 헤더 중앙 정렬
                 {'selector': 'td', 'props': [('text-align', 'center')]}]  # 데이터 중앙 정렬
            ).set_properties(**{
                'width': 'auto',  # 텍스트 길이에 맞춰 자동 조정
            })
            
            # 스타일 적용된 테이블 출력
            st.write(f"📊 {selected_site}의 고온 상세현황 (60˚C 이상 DUH_SFP List) :")
            st.dataframe(styled_df)

            # CSV 다운로드 버튼 생성
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 CSV로 다운로드",
                data=csv,
                file_name=f"{selected_site}_고온_SFP_List.csv",
                mime="text/csv"
            )

            # 해결방안 제안 문구 추가
            st.markdown("<b style='color: red;'>고온 사전조치 해결방안 제안 :</b>", unsafe_allow_html=True)

            # duh_name에 따른 해결방안 제시
            solution_df = filtered_df.groupby('duh_name').size().reset_index(name="고온 SFP 수")
            solution_df['해결방안'] = solution_df['고온 SFP 수'].apply(lambda x: 'SFP 불량 점검' if x == 1 else '냉방시설 점검 및 설치상면 조정')

            # 해결방안 테이블 출력
            st.write(solution_df)
    else:
        st.write("region, site_name, 또는 temp1 열을 찾을 수 없습니다.")
