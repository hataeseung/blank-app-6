import streamlit as st
import pandas as pd
import io

# 타이틀과 안내 메시지
st.title("🎈 통합국 DUH_SFP 고온 Report ")
st.write(
    "업로드된 데이터를 기반으로 통합국사별 60˚C 이상 고온 DUH_SFP 수량을 보여줍니다."
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
    if 'region' in df.columns and 'site_name' in df.columns and 'temp1' in df.columns:
        report_df = df[df['temp1'] >= 60].groupby(['region', 'site_name']).size().reset_index(name="high temp(60˚C 이상)")
        
        # high temp(60˚C 이상) 열의 값이 2 이상인 경우만 필터링
        report_df = report_df[report_df["high temp(60˚C 이상)"] >= 2]
        
        # 리포트 출력
        st.write("📊 통합국사별 DUH_SFP 고온 수량 Report (60˚C 이상인 SFP가 2개 이상인 경우) :")
        st.write(report_df)

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
    else:
        st.write("region, site_name, 또는 temp1 열을 찾을 수 없습니다.")