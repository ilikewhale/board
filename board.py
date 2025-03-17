import streamlit as st
import sqlite3
import time as now
import uuid
import json
import os

# DB 연동 - db이름: example.db
conn = sqlite3.connect('example.db', check_same_thread=False)  
cursor = conn.cursor()

# DB 테이블 생성
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

# 좋아요 기록 테이블 생성 (사용자가 어떤 댓글에 좋아요를 눌렀는지 기록)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS like_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        board_id INTEGER NOT NULL,
        session_id TEXT NOT NULL,
        UNIQUE(board_id, session_id)
    )
''')
conn.commit()

# 지속적인 세션 ID 관리를 위한 파일 기반 접근법
SESSION_FILE = "session_store.json"

def get_or_create_session_id():
    """파일에 저장된 세션 ID를 가져오거나 새로 생성"""
    # 1. 세션 스토어 파일 존재 확인
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
                
            # 브라우저 시그니처 생성 (간단한 식별자)
            browser_signature = get_browser_signature()
            
            # 저장된 세션 데이터에서 현재 브라우저 시그니처와 일치하는 세션 ID 찾기
            if browser_signature in session_data:
                return session_data[browser_signature]
        except:
            pass  # 파일 읽기 실패 시 새 세션 ID 생성
    
    # 2. 새 세션 ID 생성
    session_id = str(uuid.uuid4())
    
    # 3. 세션 ID 저장
    save_session_id(session_id)
    
    return session_id

def save_session_id(session_id):
    """세션 ID를 파일에 저장"""
    # 브라우저 시그니처 생성
    browser_signature = get_browser_signature()
    
    # 기존 세션 데이터 로드 또는 새로 생성
    session_data = {}
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
        except:
            pass
    
    # 브라우저 시그니처와 세션 ID 매핑
    session_data[browser_signature] = session_id
    
    # 파일에 저장
    with open(SESSION_FILE, 'w') as f:
        json.dump(session_data, f)

def get_browser_signature():
    """간단한 브라우저 시그니처 생성"""
    # 실제 환경에서는 User-Agent 등을 사용하여 더 정확한 시그니처 생성 가능
    # 여기서는 간단히 st.query_params를 사용
    return str(hash(str(st.query_params)))

# 세션 ID 초기화
if "session_id" not in st.session_state:
    st.session_state.session_id = get_or_create_session_id()

# 초기 세션 상태 설정
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_password" not in st.session_state:
    st.session_state.user_password = ""
if "user_review" not in st.session_state:
    st.session_state.user_review = ""
# 비밀번호 입력 상태 추가
if "delete_password" not in st.session_state:
    st.session_state.delete_password = {}


def local_css():
    
    st.markdown("""
    <style>
        /* 전체 폰트 및 색상 스타일 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        * {
            font-family: 'Noto Sans KR', sans-serif;
        }
        
        /* 헤더 스타일 */
        .main-header {
            background-color: #3d6aff;
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: none; 
        }
        /* .main-header 내부 글씨 색상 흰색으로 설정 */
        .main-header h1, .main-header p {
            color: white !important;
        }
                
        .body-head {
            margin-top: 1rem;
            margin-bottom: 0.5rem;       
        }
    </style>
    """, unsafe_allow_html=True)

def info():
    """안내 메시지 출력"""
    st.markdown("""
        <div class="main-header">
            <h1>📋 방명록</h1> 
            <p>
                사고닷 서비스를 이용해 보신 소감이 어떠신가요? 💭<br>
                여러분의 소중한 의견과 경험을 자유롭게 방명록에 남겨주세요!
            </p>
            <p class="body-head">
                여러분의 피드백은 저희에게 큰 힘이 됩니다 ✨
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 디버깅용 (필요시 주석 해제)
    # st.write(f"현재 세션 ID: {st.session_state.session_id}")

def render_review_form():
    """세련된 파스텔톤 스타일의 후기 작성 폼 생성"""
    
    # 세련된 CSS 스타일 적용
    st.markdown("""
<style>
    /* 폼 컨테이너 스타일 */
    .review-form-container {
        background: linear-gradient(145deg, #f4f8fa, #f4f7f9);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
    }
    
    /* 제목 스타일 */
    .form-header {
        color: #3498db;
        font-weight: 600;
        font-size: 30 rem;
        margin-bottom: 20px;
        font-family: 'Helvetica Neue', sans-serif;
        letter-spacing: 0.5px;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput input, .stTextArea textarea {
        border: 1px solid #e3e3e3;
        border-radius: 8px;
        padding: 10px 12px;
        background-color: #ffffff;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        color: black;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(33, 150, 243, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
    }
    
    /* 폼 레이블 스타일 */
    .css-q8sbsg p {
        font-weight: 500;
        color: #484848;
        margin-bottom: 4px;
    }
</style>
    """, unsafe_allow_html=True)
    
    # 폼 컨테이너 시작
    st.write("### 사용자 후기")
    # st.markdown('<p class="form-header">사용자 후기</p>', unsafe_allow_html=True)
    
    # 폼 내용
    with st.form(key='review_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            user_name = st.text_input(
                "이름", 
                value=st.session_state.user_name if "user_name" in st.session_state else "", 
                key="user_name",
                placeholder="이름을 입력해주세요"
            )
        
        with col2:
            user_password = st.text_input(
                "비밀번호", 
                type="password", 
                value=st.session_state.user_password if "user_password" in st.session_state else "", 
                key="user_password",
                placeholder="비밀번호를 입력해주세요"
            )
        
        user_review = st.text_area(
            "후기 작성", 
            value=st.session_state.user_review if "user_review" in st.session_state else "", 
            key="user_review",
            placeholder="여기에 후기를 작성해주세요...",
            height=120
        )
        

        submit_button = st.form_submit_button("후기 제출")
    
    # 폼 컨테이너 종료
    st.markdown('</div>', unsafe_allow_html=True)
    
    return user_name, user_password, user_review, submit_button

def handle_review_submission(user_name, user_password, user_review):
    """후기 제출 시 DB 저장"""
    if user_name and user_password and user_review:
        cursor.execute("INSERT INTO boards (board_name, password, comment) VALUES (?, ?, ?)", (user_name, user_password, user_review))
        conn.commit()
        
        st.success("소중한 후기 감사합니다 😊")

        # 세션 상태 초기화
        for key in ["user_name", "user_password", "user_review"]:
            if key in st.session_state:
                del st.session_state[key]

        now.sleep(1)
        st.rerun()
    else:
        st.error("이름과 비밀번호, 후기를 모두 작성해 주세요.")

def display_reviews():
    """저장된 후기 목록을 출력"""
    # CSS 스타일 정의
    st.markdown("""
    <style>
    /* 리뷰 박스 스타일 */
    .review-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* 버튼 컨테이너 스타일 */
    .btn-container {
        display: flex;
        gap: 10px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    
    /* 버튼 기본 스타일 */
    .custom-btn {
        color: white;
        border: none;
        border-radius: 20px;
        padding: 5px 15px;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* 호버 효과 */
    .custom-btn:hover {
        opacity: 0.8;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* 비활성화된 버튼 */
    .disabled-btn {
        background-color: #cccccc;
        cursor: not-allowed;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 세션 상태 초기화
    if 'active_form' not in st.session_state:
        st.session_state.active_form = None
    
    st.write("### 방명록")
    
    # 모든 리뷰 불러오기
    cursor.execute("SELECT * FROM boards ORDER BY board_id DESC")
    all_reviews = cursor.fetchall()

    # 각 리뷰 표시
    for idx, row in enumerate(all_reviews):
        review_id, name, password, review, likes = row[:5]

        # 리뷰 박스 생성
        st.markdown(f"""
        <div class="review-box">
            <h4>💙 {name}님의 리뷰</h4>
            <p><strong>후기 내용:</strong> {review}</p>
            <p>좋아요 수: {likes}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 좋아요 버튼 상태 확인
        cursor.execute("SELECT * FROM like_records WHERE board_id = ? AND session_id = ?", 
                      (review_id, st.session_state.session_id))
        already_liked = cursor.fetchone() is not None
        
        # 버튼 생성
        col1, col2, col3 = st.columns(3)
        
        # 좋아요 버튼
        like_button = col1.button(
            "👍 이미 좋아요" if already_liked else "👍 좋아요", 
            key=f"like_{idx}",
            disabled=already_liked,
        )
        
        # 수정 버튼
        edit_button = col2.button("✏️ 수정", key=f"edit_{idx}")
        
        # 삭제 버튼
        delete_button = col3.button("🗑️ 삭제", key=f"delete_{idx}")

        # 좋아요 버튼 처리
        if like_button:
            handle_like(review_id)

        # 수정 버튼 처리
        if edit_button:
            # 모든 다른 폼 닫기
            for r_id in [r[0] for r in all_reviews]:
                if f"show_delete_form_{r_id}" in st.session_state:
                    del st.session_state[f"show_delete_form_{r_id}"]
                if r_id != review_id and f"show_edit_form_{r_id}" in st.session_state:
                    del st.session_state[f"show_edit_form_{r_id}"]
                    if f"edit_verified_{r_id}" in st.session_state:
                        del st.session_state[f"edit_verified_{r_id}"]
            
            # 현재 폼 활성화
            st.session_state.active_form = f"edit_{review_id}"
            st.session_state[f"show_edit_form_{review_id}"] = True
            
        # 수정 폼 표시
        if st.session_state.get(f"show_edit_form_{review_id}", False):
            with st.container():
                # 수정 폼 헤더
                st.markdown("""
                <div style="background-color: #f1f8e9; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h5>리뷰 수정</h5>
                </div>
                """, unsafe_allow_html=True)
                
                # 비밀번호 입력 필드
                password_input = st.text_input(
                    "비밀번호를 입력하세요", 
                    type="password", 
                    key=f"edit_pwd_{review_id}"
                )
                
                # 비밀번호 인증 완료 시 수정 폼
                if st.session_state.get(f"edit_verified_{review_id}", False):
                    new_review = st.text_area(
                        "수정할 내용", 
                        value=review, 
                        key=f"edit_content_{review_id}"
                    )
                    
                    # 저장 및 취소 버튼
                    col1, col2 = st.columns(2)
                    save_button = col1.button("💾 저장", key=f"save_{review_id}")
                    cancel_button = col2.button("❌ 취소", key=f"cancel_{review_id}")
                    
                    # 저장 버튼 처리
                    if save_button:
                        cursor.execute(
                            "UPDATE boards SET comment = ?, updated_at = CURRENT_TIMESTAMP WHERE board_id = ?", 
                            (new_review, review_id)
                        )
                        conn.commit()
                        
                        # 상태 초기화
                        del st.session_state[f"show_edit_form_{review_id}"]
                        del st.session_state[f"edit_verified_{review_id}"]
                        st.session_state.active_form = None
                        st.success("리뷰가 수정되었습니다.")
                        now.sleep(1)
                        st.rerun()
                    
                    # 취소 버튼 처리
                    if cancel_button:
                        del st.session_state[f"show_edit_form_{review_id}"]
                        del st.session_state[f"edit_verified_{review_id}"]
                        st.session_state.active_form = None
                        st.rerun()
                else:
                    # 비밀번호 확인 및 취소 버튼
                    verify_col1, verify_col2 = st.columns(2)
                    verify_button = verify_col1.button("🔑 비밀번호 확인", key=f"verify_edit_{review_id}")
                    cancel_edit_button = verify_col2.button("❌ 취소", key=f"cancel_edit_init_{review_id}")
                    
                    # 비밀번호 확인 처리
                    if verify_button:
                        if password_input == password:
                            st.session_state[f"edit_verified_{review_id}"] = True
                            st.success("비밀번호가 확인되었습니다. 내용을 수정해주세요.")
                            st.rerun()
                        else:
                            st.error("비밀번호가 일치하지 않습니다.")
                    
                    # 취소 버튼 처리
                    if cancel_edit_button:
                        del st.session_state[f"show_edit_form_{review_id}"]
                        st.session_state.active_form = None
                        st.rerun()

        # 삭제 버튼 처리
        if delete_button:
            # 모든 다른 폼 닫기
            for r_id in [r[0] for r in all_reviews]:
                if f"show_edit_form_{r_id}" in st.session_state:
                    del st.session_state[f"show_edit_form_{r_id}"]
                    if f"edit_verified_{r_id}" in st.session_state:
                        del st.session_state[f"edit_verified_{r_id}"]
                if r_id != review_id and f"show_delete_form_{r_id}" in st.session_state:
                    del st.session_state[f"show_delete_form_{r_id}"]
            
            # 현재 폼 활성화
            st.session_state.active_form = f"delete_{review_id}"
            st.session_state[f"show_delete_form_{review_id}"] = True
            
        # 삭제 폼 표시
        if st.session_state.get(f"show_delete_form_{review_id}", False):
            with st.container():
                # 삭제 폼 헤더
                st.markdown("""
                <div style="background-color: #ffebee; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h5>리뷰 삭제</h5>
                </div>
                """, unsafe_allow_html=True)
                
                # 비밀번호 입력 필드
                password_input = st.text_input(
                    "비밀번호를 입력하세요", 
                    type="password", 
                    key=f"del_pwd_{review_id}"
                )
                
                # 확인 및 취소 버튼
                del_col1, del_col2 = st.columns(2)
                confirm_button = del_col1.button("✓ 확인", key=f"confirm_del_{review_id}")
                cancel_button = del_col2.button("❌ 취소", key=f"cancel_del_{review_id}")
                
                # 확인 버튼 처리
                if confirm_button:
                    delete_with_password(review_id, name, password, password_input)
                    st.session_state.active_form = None
                
                # 취소 버튼 처리
                if cancel_button:
                    del st.session_state[f"show_delete_form_{review_id}"]
                    st.session_state.active_form = None
                    st.rerun()
        
        # 리뷰 사이에 구분선 추가
        st.markdown("<hr style='margin: 20px 0; opacity: 0.3;'>", unsafe_allow_html=True)

def handle_like(review_id):
    """좋아요 버튼 클릭 시 좋아요 수 증가 (중복 방지)"""
    session_id = st.session_state.session_id
    
    # 이미 좋아요를 눌렀는지 확인
    cursor.execute("SELECT * FROM like_records WHERE board_id = ? AND session_id = ?", 
                  (review_id, session_id))
    
    existing_like = cursor.fetchone()
    
    if existing_like is None:  # 아직 좋아요를 누르지 않았다면
        try:
            # 좋아요 수 증가
            cursor.execute("UPDATE boards SET likes = likes + 1 WHERE board_id = ?", (review_id,))
            
            # 좋아요 기록 추가
            cursor.execute("INSERT INTO like_records (board_id, session_id) VALUES (?, ?)", 
                          (review_id, session_id))
            
            conn.commit()
            st.success("좋아요를 눌렀습니다!")
        except sqlite3.Error as e:
            st.error(f"데이터베이스 오류: {e}")
            conn.rollback()
    else:
        st.warning("이미 좋아요를 누른 댓글입니다.")
    
    # 1초 대기 후 페이지 새로고침
    now.sleep(1)
    st.rerun()

def delete_with_password(review_id, name, stored_password, input_password):
    """비밀번호 확인 후 댓글 삭제"""
    if input_password == stored_password:
        # 비밀번호가 일치하면 삭제
        cursor.execute("DELETE FROM boards WHERE board_id = ?", (review_id,))
        # 관련 좋아요 기록도 삭제
        cursor.execute("DELETE FROM like_records WHERE board_id = ?", (review_id,))
        conn.commit()
        
        # 삭제 폼 상태 초기화
        if f"show_delete_form_{review_id}" in st.session_state:
            del st.session_state[f"show_delete_form_{review_id}"]
            
        st.success(f"{name}님의 리뷰가 삭제되었습니다.")
        now.sleep(1)
        st.rerun()
    else:
        st.error("비밀번호가 일치하지 않습니다.")

def display_sidebar():
    """사이드바를 표시하는 함수"""
    with st.sidebar:
        # 로고 및 타이틀
        st.markdown("<h1 style='font-size:120px;'>⚖️</h1>", unsafe_allow_html=True)
        st.title("사고닷 방명록")
        st.markdown('사고닷 서비스를 이용해주셔서 감사합니다. 여러분의 소중한 의견을 남겨주세요.', unsafe_allow_html=True)         
        
        st.divider()
        
        # 카운터 표시 (총 후기 갯수와 총 좋아요 갯수)
        st.subheader("📊 한눈에 보기")
        
        # 총 후기 갯수 
        cursor.execute("SELECT COUNT(*) FROM boards")
        total_reviews = cursor.fetchone()[0]
        st.metric(label="총 후기 갯수", value=f"{total_reviews}개")
        
        # 총 좋아요 갯수
        cursor.execute("SELECT SUM(likes) FROM boards")
        total_likes = cursor.fetchone()[0] or 0  # 이 함수는 별도로 구현해야 함
        st.metric(label="총 좋아요 갯수", value=f"{total_likes}개")
        
        st.divider()
        
        # 연락처 정보
        st.caption("고객센터: 02-1004-1004")
        st.caption("이메일: sagodot@example.com")
        st.caption("© 2025 사고닷. All rights reserved.")


def main():
    """메인 실행 함수"""
    local_css() 
    info()


    # 후기 작성 폼 실행
    user_name, user_password, user_review, submit_button = render_review_form()
    
    # 제출 버튼 클릭 시 처리
    if submit_button:
        handle_review_submission(user_name, user_password, user_review)

    # 저장된 리뷰 목록 표시
    display_reviews()

    # 사이드바 추가
    display_sidebar()

if __name__ == "__main__":
    main()
