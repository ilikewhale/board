import streamlit as st
import sqlite3

# DB 연동 - db이름: example.db
conn = sqlite3.connect('board/example.db') # + db의 위치 고정 필요 
cursor = conn.cursor()

# DB에 테이블 생성 - 속성: board_id(PK), 이름, 리뷰
# + 테이블 이름 복수형으로 변경 board -> boards
# + 생성 날짜(created_at), 수정(updated_at) 날짜 추가
# + 컬럼 이름 수정 : 이름 -> board_name, 내용 -> comment 
cursor.execute('''
    CREATE TABLE IF NOT EXISTS boards (
        board_id INTEGER PRIMARY KEY AUTOINCREMENT,
        board_name VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        comment TEXT NOT NULL,
        likes INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
# SQLlite는 commit을 꼭 해줘야한대~
conn.commit()

# 팀 소개
def team_intro():
    st.header("우리 팀 소개")
    st.write("""
    우리는 혁신적인 서비스를 제공하는 팀입니다. 다양한 분야에서 경험을 가진 전문가들이 모여,
    고객에게 최고의 경험을 선사하기 위해 노력하고 있습니다.
    """)

# 서비스 소개
def service_intro():
    st.header("우리가 만든 서비스")
    st.write("""
    우리의 서비스는 사용자에게 실용적이고 편리한 기능을 제공합니다. 직관적인 인터페이스와
    효율적인 문제 해결을 위해 항상 최선을 다하고 있습니다.
    """)

# 후기 작성
def new_geustbook():
    st.header("사용자 후기")
    
    # 후기 작성 폼
    with st.form(key='review_form'):
        user_name = st.text_input("이름") # 이름 작성하는 칸 생성
        user_password = st.text_input("비밀번호") # + 비밀번호 작성 칸 생성
        user_review = st.text_area("후기 작성") # 후기 작성 칸 생성
        submit_button = st.form_submit_button("후기 제출") # 후기 제출 버튼 생성
    
    # 후기 제출 버튼 누른 후기 DB에 저장하기
    if submit_button:
        if user_name and user_password and user_review:
            st.success("소중한 후기 감사합니다")
            cursor.execute("INSERT INTO boards (board_name, password, comment) VALUES (?, ?, ?)", (user_name, user_password, user_review)) #DB에 저장하기
            conn.commit() # DB 변경 사항 저장
        else:
            st.error("이름과 후기를 모두 작성해 주세요.") # 이름이나 후기가 작성되지 않은 경우

    # 제출된 후기 표시 (새로운 후기 먼저 표시)
    st.write("### 제출된 후기들")

    cursor.execute("SELECT * FROM boards") # DB에서 정보 가져오기
    all_review = cursor.fetchall() # DB 정보들 all_review 변수로 선언

    # 제출된 리뷰 보기 & 삭제하기 & 편집하기
    for idx, row in enumerate(all_review):
        review_id = row[0]
        name = row[1]  # 첫 번째 열은 '이름'
        review = row[2]  # 두 번째 열은 '리뷰'
        
        password = row[3] # + 비밀번호
        likes = row[4] # + 좋아요 수

        print(row) # + 조회 결과 표시 - 데이터 확인
        st.write(f"💛 {name}님: {review}")
        st.write(f"좋아요 수: {likes}") # + 좋아요 표시 기능 추가

        left_column, right_column = st.columns(2) 

        edit_button = left_column.button("편집", key=f"edit_{idx}") # 리뷰 편집 버튼
        delete_button = right_column.button("삭제", key=f"delete_{idx}") # 리뷰 삭제 버튼

    # 삭제 버튼 클릭 시 리뷰 삭제
    # + -> 여기서 비밀번호 일치 여부 확인 구현하면 됩니당 !!
        if delete_button:
            cursor.execute("DELETE FROM boards WHERE board_id = ?", (review_id, ))
            conn.commit()  # 변경사항을 DB에 적용
            st.write(f"{name}님의 리뷰가 삭제되었습니다.")
            st.rerun()  # 페이지 새로 고침
    # 편집 버튼 클릭 시 리뷰 수정
        elif edit_button:
            edit_name = st.text_input("이름")
            edir_review = st.text_area("후기 작성")
            save_button = st.button("후기 제출")  

# Streamlit 페이지 구조
def main():
    st.title("우리 서비스 웹페이지")
    
    # 각 섹션 호출
    team_intro()
    service_intro()
    new_geustbook()

if __name__ == "__main__":
    main()
