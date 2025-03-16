import streamlit as st
import sqlite3
import time

now = time

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

# + 세션 정보를 이용해 폼 초기화를 위한 초기 세션 정보 저장
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_password" not in st.session_state:
    st.session_state.user_password = ""
if "user_review" not in st.session_state:
    st.session_state.user_review = ""

def info():
    st.write('''사고닷을 사용해주셔서 감사합니다! 방명록을 남겨주세요 💖''')

# 후기 작성
def new_geustbook():
    st.header("사용자 후기")
    
    # 후기 작성 폼
    with st.form(key='review_form'):
        user_name = st.text_input("이름", value=st.session_state.user_name, key="user_name") # 이름 작성하는 칸 생성
        user_password = st.text_input("비밀번호", type="password", value=st.session_state.user_password, key="user_password") # + 비밀번호 작성 칸 생성
        user_review = st.text_area("후기 작성", value=st.session_state.user_review, key="user_review") # 후기 작성 칸 생성
        submit_button = st.form_submit_button("후기 제출") # 후기 제출 버튼 생성
    
    # 후기 제출 버튼 누른 후기 DB에 저장하기
    if submit_button:
        if user_name and user_password and user_review:
            st.success("소중한 후기 감사합니다 😊")
            cursor.execute("INSERT INTO boards (board_name, password, comment) VALUES (?, ?, ?)", (user_name, user_password, user_review)) #DB에 저장하기
            conn.commit() # DB 변경 사항 저장

            del st.session_state["user_name"]
            del st.session_state["user_password"]
            del st.session_state["user_review"]

            now.sleep(1)
            st.rerun()
        else:
            st.error("이름과 후기를 모두 작성해 주세요.") # 이름이나 후기가 작성되지 않은 경우

    # 제출된 후기 표시 (새로운 후기 먼저 표시)
    st.write("### 방명록")

    cursor.execute("SELECT * FROM boards ORDER BY board_id DESC") # DB에서 정보 가져오기
    all_review = cursor.fetchall() # DB 정보들 all_review 변수로 선언

    # 제출된 리뷰 보기 & 삭제하기 & 편집하기
    for idx, row in enumerate(all_review):
        review_id = row[0]
        name = row[1]  # 이름
        #password = row[2] # + 비밀번호
        review = row[3]  # 리뷰
        likes = row[4] # + 좋아요 수

        print(row) # + 조회 결과 표시 - 데이터 확인

        with st.expander(f"💛 {name}님의 리뷰"):  # 각 리뷰는 펼침(expander) 형식으로 보여줍니다
            st.write(f"**후기 내용:** {review}")
            st.write(f"좋아요 수: {likes}")

            left_column, right_column = st.columns(2) 
            like_button = left_column.button("좋아요", key=f"like_{idx}") # + 좋아요 버튼
            delete_button = right_column.button("삭제", key=f"delete_{idx}") # 리뷰 삭제 버튼

            #edit_button = left_column.button("편집", key=f"edit_{idx}") # 리뷰 편집 버튼

            # + 좋아요 버튼 클릭 시 좋아요 + 1
            if like_button:
                cursor.execute("SELECT likes FROM boards WHERE board_id = ?", (review_id, ))
                one_review = cursor.fetchall()
                total_like = int(one_review[0][0]) + 1 # + 좋아요 증가
                cursor.execute("UPDATE boards SET likes = ? WHERE board_id = ?", (total_like, review_id))
                conn.commit()
                st.rerun()

            # 삭제 버튼 클릭 시 리뷰 삭제
            # + -> 여기서 비밀번호 일치 여부 확인 구현하면 됩니당 !!
            if delete_button:
                cursor.execute("DELETE FROM boards WHERE board_id = ?", (review_id, ))
                conn.commit()  # 변경사항을 DB에 적용
                st.write(f"{name}님의 리뷰가 삭제되었습니다.")
                st.rerun()  # 페이지 새로 고침
        # 편집 버튼 클릭 시 리뷰 수정
        #   elif edit_button:
        #    ### 오류 있음
        #    edir_password = st.text_input("비밀번호", type="password")
        #    edir_review = st.text_area("후기 수정")
        #    save_button = st.button("후기 저장")
        #    if save_button:
        #        if (edir_password == password):
        #            cursor.execute("UPDATE boards SET comment = ? WHERE board_id = ?", (edir_review, review_id, ))
        #            conn.commit()

        #            st.success("성공적으로 수정했습니다.")
        #        else:
        #            st.error("비밀번호가 일치하지 않습니다.")

# Streamlit 페이지 구조
def main():
    st.title("사고닷 방명록")
    info()
    # 각 섹션 호출
    new_geustbook()

if __name__ == "__main__":
    main()
