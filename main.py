from flask import Flask, request, jsonify
from config import Config
from features.gemini_ai import GeminiAI
from features.games import GameManager
from features.weather import WeatherManager
import logging
import os
from datetime import datetime

app = Flask(__name__)

# 각 매니저 인스턴스 생성
game_manager = GameManager()
weather_manager = WeatherManager()

# 로깅 설정 개선
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_simple_text_response(text):
    """간단한 텍스트 응답 생성"""
    return {
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": text
                }
            }]
        }
    }

def create_error_response(error_message="처리 중 오류가 발생했습니다. 다시 시도해주세요."):
    """에러 응답 생성"""
    return create_simple_text_response(error_message)

def extract_user_info(data):
    """요청 데이터에서 사용자 및 방 정보 추출"""
    try:
        user_message = data['userRequest']['utterance']
        user_id = data['userRequest']['user']['id']
        
        # 방 정보 추출 (카카오톡 챗봇에서 제공)
        # 개인톡과 단체방을 구분
        room_id = data.get('userRequest', {}).get('block', {}).get('id', 'private')
        if not room_id:
            room_id = f"room_{hash(str(data.get('userRequest', {})))}"
        
        return user_message, user_id, room_id
    except KeyError as e:
        logger.error(f"요청 데이터 파싱 오류: {e}")
        raise ValueError("잘못된 요청 형식입니다.")

@app.route('/webhook', methods=['POST'])
def webhook():
    """카카오톡 챗봇 웹훅 엔드포인트"""
    try:
        # 요청 데이터 검증
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다."))
        
        user_message, user_id, room_id = extract_user_info(data)
        logger.info(f"방({room_id}) 사용자({user_id}) 메시지: {user_message}")
        
        # 메시지 전처리
        user_message = user_message.strip()
        command_parts = user_message.split()
        
        # 빈 메시지 처리
        if not user_message:
            return jsonify(create_simple_text_response("메시지를 입력해주세요."))
        
        # 명령어 라우팅
        ai_response = route_command(user_id, room_id, user_message, command_parts)
        
        return jsonify(create_simple_text_response(ai_response))
        
    except ValueError as e:
        logger.error(f"데이터 검증 오류: {e}")
        return jsonify(create_error_response(str(e)))
    except Exception as e:
        logger.error(f"웹훅 처리 오류: {e}")
        return jsonify(create_error_response())

def get_korean_cities():
    """한국 도시 목록 반환"""
    return [
        # 특별시
        '서울',
        
        # 광역시
        '부산', '대구', '인천', '광주', '대전', '울산',
        
        # 특별자치시
        '세종',
        
        # 경기도
        '수원', '성남', '용인', '안양', '안산', '과천', '광명', '광주', '군포', '부천',
        '시흥', '김포', '안성', '오산', '의왕', '이천', '평택', '하남', '화성', '여주',
        '양평', '고양', '구리', '남양주', '동두천', '양주', '의정부', '파주', '포천',
        '가평', '연천',
        
        # 강원도
        '춘천', '원주', '강릉', '동해', '태백', '속초', '삼척',
        '홍천', '횡성', '영월', '평창', '정선', '철원', '화천', '양구', '인제', '고성', '양양',
        
        # 충청북도
        '청주', '충주', '제천',
        '보은', '옥천', '영동', '증평', '진천', '괴산', '음성', '단양',
        
        # 충청남도
        '천안', '공주', '보령', '아산', '서산', '논산', '계룡', '당진',
        '금산', '부여', '서천', '청양', '홍성', '예산', '태안',
        
        # 전라북도
        '전주', '군산', '익산', '정읍', '남원', '김제',
        '완주', '진안', '무주', '장수', '임실', '순창', '고창', '부안',
        
        # 전라남도
        '목포', '여수', '순천', '나주', '광양',
        '담양', '곡성', '구례', '고흥', '보성', '화순', '장흥', '강진', '해남', '영암',
        '무안', '함평', '영광', '장성', '완도', '진도', '신안',
        
        # 경상북도
        '포항', '경주', '김천', '안동', '구미', '영주', '영천', '상주', '문경', '경산',
        '군위', '의성', '청송', '영양', '영덕', '청도', '고령', '성주', '칠곡',
        '예천', '봉화', '울진', '울릉',
        
        # 경상남도
        '창원', '진주', '통영', '사천', '김해', '밀양', '거제', '양산',
        '의령', '함안', '창녕', '고성', '남해', '하동', '산청', '함양', '거창', '합천',
        
        # 제주특별자치도
        '제주', '서귀포',
        
        # 서울 구
        '종로구', '중구', '용산구', '성동구', '광진구', '동대문구', '중랑구', '성북구',
        '강북구', '도봉구', '노원구', '은평구', '서대문구', '마포구', '양천구', '강서구',
        '구로구', '금천구', '영등포구', '동작구', '관악구', '서초구', '강남구', '송파구', '강동구',
        
        # 기타 자주 사용되는 별칭들
        '판교', '분당', '일산', '평촌', '중계', '잠실', '강남', '홍대', '명동', '이태원',
        '신촌', '압구정', '청담', '역삼', '삼성', '선릉', '건대', '성수', '왕십리',
        '용산', '한남', '여의도', '마포', '상암', '목동', '영등포', '신림', '사당',
        '교대', '서초', '잠원', '반포', '한강', '송파', '문정', '석촌', '방이',
        '둔촌', '천호', '길동', '상일', '명일', '고덕', '암사', '천왕', '풍납',
        
        # 신도시 및 개발지구
        '동탄', '광교', '김포신도시', '파주신도시', '운정', '검단신도시', '청라',
        '송도', '영종도', '세종신도시', '오창', '진천', '혁신도시'
    ]

def get_world_cities():
    """해외 도시 목록 반환 (영어 + 한글)"""
    english_cities = [
        'tokyo', 'osaka', 'beijing', 'shanghai', 'hongkong', 'singapore',
        'bangkok', 'manila', 'jakarta', 'kualalumpur', 'hanoi', 'hochiminh',
        'newyork', 'losangeles', 'chicago', 'houston', 'philadelphia',
        'london', 'paris', 'berlin', 'rome', 'madrid', 'amsterdam',
        'zurich', 'vienna', 'prague', 'budapest', 'warsaw', 'stockholm',
        'oslo', 'copenhagen', 'helsinki', 'dublin', 'lisbon', 'athens',
        'istanbul', 'moscow', 'sydney', 'melbourne', 'brisbane', 'perth',
        'auckland', 'wellington', 'vancouver', 'toronto', 'montreal',
        'dubai', 'doha', 'riyadh', 'cairo', 'casablanca', 'johannesburg',
        'nairobi', 'lagos', 'accra', 'addisababa', 'mumbai', 'delhi',
        'bangalore', 'kolkata', 'chennai', 'hyderabad', 'sao paulo',
        'rio de janeiro', 'brasilia', 'salvador', 'fortaleza', 'belo horizonte'
    ]
    
    korean_cities = [
        '도쿄', '오사카', '베이징', '상하이', '홍콩', '싱가포르',
        '방콕', '마닐라', '자카르타', '쿠알라룸푸르', '하노이', '호치민',
        '뉴욕', '로스앤젤레스', '시카고', '휴스턴', '필라델피아',
        '런던', '파리', '베를린', '로마', '마드리드', '암스테르담',
        '취리히', '비엔나', '프라하', '부다페스트', '바르샤바', '스톡홀름',
        '오슬로', '코펜하겐', '헬싱키', '더블린', '리스본', '아테네',
        '이스탄불', '모스크바', '시드니', '멜번', '브리즈번', '퍼스',
        '오클랜드', '웰링턴', '밴쿠버', '토론토', '몬트리올',
        '두바이', '도하', '리야드', '카이로', '카사블랑카', '요하네스버그',
        '나이로비', '라고스', '아크라', '아디스아바바', '뭄바이', '델리'
    ]
    
    return english_cities + korean_cities

def is_city_command(command):
    """도시명 명령어인지 확인"""
    if not command.startswith('/'):
        return False
    
    city_name = command[1:]  # '/' 제거
    
    korean_cities = get_korean_cities()
    world_cities = get_world_cities()
    
    # 대소문자 구분 없이 확인
    city_lower = city_name.lower()
    world_cities_lower = [city.lower() for city in world_cities]
    
    return (city_name in korean_cities or 
            city_lower in world_cities_lower)

def route_command(user_id, room_id, user_message, command_parts):
    """명령어 라우팅 처리 - /질문 명령어 적용"""
    try:
        # AI 질문 명령어
        if command_parts[0].startswith('/질문'):
            if len(command_parts) > 1:
                question = ' '.join(command_parts[1:])
                return GeminiAI.get_response(question, f"{room_id}_{user_id}")
            else:
                return """🤖 **AI 질문하기**
                
💬 **사용법:**
`/질문 [질문내용]`

📝 **예시:**
• `/질문 파이썬 공부법 알려줘`
• `/질문 영어 번역해줘: 안녕하세요`
• `/질문 재미있는 이야기 해줘`
• `/질문 오늘 뭐 먹을까?`

무엇이든 궁금한 걸 물어보세요! ✨"""
        
        # 기존 /숨, /AI 명령어는 메뉴용으로만
        elif (command_parts[0].startswith('/숨') or 
              command_parts[0].startswith('/AI') or
              command_parts[0].startswith('/ai')):
            return handle_main_command(user_id, room_id, command_parts)
        
        # 점심 추천 명령어 처리
        elif command_parts[0] == '/점심추천':
            return game_manager.lunch_recommendation(room_id)
        
        # 날씨 명령어 처리
        elif command_parts[0].startswith('/날씨'):
            return weather_manager.parse_weather_command(command_parts)
        
        # 게임 명령어 처리
        elif command_parts[0].startswith('/게임'):
            return game_manager.parse_game_command(user_id, room_id, command_parts)
        
        # 도시명 직접 입력으로 날씨 조회
        elif is_city_command(command_parts[0]):
            city_name = command_parts[0][1:]  # '/' 제거
            return weather_manager.parse_weather_command(['/날씨', city_name])
        
        # 특별한 명령어 처리
        elif user_message.lower() in ['도움말', 'help']:
            return get_main_menu()
        
        # 일반 메시지 - AI 호출 안함
        else:
            return """🤖 **숨.AI 사용법**
            
🧠 **AI에게 질문:**
• `/질문 [질문내용]` - AI와 대화

🎯 **바로 사용:**  
• `/점심추천` - 점심 메뉴 추천
• `/게임` - 게임 센터
• `/서울`, `/부산` - 날씨 조회
• `/숨` 또는 `/AI` - 전체 메뉴

📝 **예시:**
• `/질문 파이썬 공부법 알려줘`
• `/질문 재미있는 농담 해줘`

어떤 기능을 사용하시겠어요? ✨"""
            
    except Exception as e:
        logger.error(f"명령어 처리 오류: {e}")
        return "명령어 처리 중 오류가 발생했습니다."

def handle_main_command(user_id, room_id, command_parts):
    """/숨 또는 /AI 명령어 처리"""
    if len(command_parts) == 1:
        # 기본 명령어
        return get_main_menu()
    
    sub_command = command_parts[1].lower()
    
    if sub_command in ['도움말', 'help', '도움']:
        return get_help_message()
    elif sub_command in ['게임', 'game']:
        return game_manager.parse_game_command(user_id, room_id, ['/게임'])
    elif sub_command in ['날씨', 'weather']:
        if len(command_parts) >= 3:
            return weather_manager.parse_weather_command(['/날씨'] + command_parts[2:])
        else:
            return weather_manager.parse_weather_command(['/날씨'])
    elif sub_command in ['정보', 'info', '버전']:
        return get_bot_info()
    elif sub_command in ['초기화', 'reset', '리셋']:
        GeminiAI.clear_conversation(f"{room_id}_{user_id}")
        return "🔄 대화 기록이 초기화되었습니다!"
    else:
        return f"알 수 없는 명령어입니다: {sub_command}\n\n{get_main_menu()}"

def get_main_menu():
    """메인 메뉴"""
    return """🤖 **숨.AI 메인 메뉴**

🧠 **AI 질문:**
• `/질문 [질문내용]` - AI와 대화하기

📋 **빠른 명령어:**
• `/숨 도움말` - 전체 사용법
• `/숨 게임` - 게임 센터  
• `/숨 날씨 [도시명]` - 날씨 정보
• `/숨 정보` - 봇 정보 확인
• `/숨 초기화` - 대화 기록 삭제

🍽️ **점심 추천:**
• `/점심추천` - 오늘 점심 메뉴 추천 (200가지)

🌤️ **간편 날씨:**
• `/서울`, `/부산`, `/제주` - 국내 도시
• `/tokyo`, `/newyork` - 해외 도시

📝 **사용 예시:**
• `/질문 파이썬 공부법 알려줘`
• `/질문 영어 번역해줘: 안녕하세요`
• `/점심추천`
• `/서울`

어떤 기능을 사용하시겠어요? ✨"""

def get_help_message():
    """도움말 메시지"""
    return """🤖 **숨.AI (ver 1.0) 사용법**

🧠 **AI와 대화:**
• `/질문 [질문내용]` - AI에게 무엇이든 물어보세요!

📝 **질문 예시:**
• `/질문 파이썬 공부법 알려줘`
• `/질문 영어 번역해줘: 오늘 날씨가 좋네요`
• `/질문 재미있는 이야기 해줘`
• `/질문 수학 문제 풀어줘`
• `/질문 요리 레시피 추천해줘`

🔧 **메인 명령어:**
• `/숨` - 메인 메뉴
• `/숨 도움말` - 이 메시지
• `/숨 게임` - 게임 센터
• `/숨 초기화` - AI 대화 기록 삭제

🎮 **게임 & 엔터테인먼트:**
• `/게임` - 7가지 미니게임
• `/점심추천` - 200가지 메뉴 중 추천

🌤️ **날씨 정보:**
• `/서울`, `/부산` - 간편 조회
• `/날씨 [도시명]` - 상세 정보

💡 **팁:** 
• AI 대화는 `/질문`으로만 시작하세요!
• 다른 메시지는 AI 호출 없이 안내만 제공합니다.

무엇을 도와드릴까요? ✨"""

def get_bot_info():
    """봇 정보"""
    return """🤖 **숨.AI 정보**
🏷️ **버전**: v1.0
🧠 **AI 엔진**: Google Gemini
⚡ **주요 기능**: 
  - 지능형 대화 AI
  - 미니게임 센터 (7가지 게임)
  - 실시간 날씨 정보
  - 점심 메뉴 추천 (200가지)
  - 전국 도시별 날씨 조회
🎮 **게임 통계**:
  - 밸런스 게임: 100가지
  - 수수께끼: 12가지
  - 점수 시스템 및 랭킹
🛠️ **개발 상태**: 정식 운영
📅 **업데이트**: 지속적 개선 중
🌍 **지원 도시**: 전국 226개 지역 + 해외 주요 도시
📊 **특별 기능**:
  - 시간대별 맞춤 응답
  - 사용자별 게임 통계
  - 연속 출석 보너스
궁금한 점이 있으시면 언제든 물어보세요! 😊"""

@app.route('/', methods=['GET'])
def home():
    """홈페이지"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>숨 AI Bot v1.0</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .feature { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .stats { display: flex; justify-content: space-around; margin: 20px 0; }
            .stat { text-align: center; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 숨 AI Bot v1.0</h1>
            <p style="text-align: center; font-size: 18px;">서버가 정상적으로 실행 중입니다! 🚀</p>
            
            <div class="stats">
                <div class="stat">
                    <h3>🎮 게임</h3>
                    <p>7종류</p>
                </div>
                <div class="stat">
                    <h3>🍽️ 메뉴</h3>
                    <p>200가지</p>
                </div>
                <div class="stat">
                    <h3>🌍 도시</h3>
                    <p>300+ 지역</p>
                </div>
                <div class="stat">
                    <h3>⚖️ 밸런스</h3>
                    <p>100가지</p>
                </div>
            </div>
            
            <div class="feature">
                <h3>🔧 주요 기능</h3>
                <ul>
                    <li><strong>AI 대화</strong> - Google Gemini 기반 지능형 대화</li>
                    <li><strong>게임 센터</strong> - 7가지 미니게임과 랭킹 시스템</li>
                    <li><strong>날씨 정보</strong> - 전국 + 해외 실시간 날씨</li>
                    <li><strong>점심 추천</strong> - 200가지 메뉴 중 랜덤 추천</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>🎯 바로 사용하기</h3>
                <p><code>/질문 [질문내용]</code> - AI와 대화</p>
                <p><code>/점심추천</code> - 점심 메뉴 추천</p>
                <p><code>/서울</code> - 서울 날씨</p>
                <p><code>/게임</code> - 게임 센터</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/health">🔍 서버 상태 확인</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "features": {
            "AI Chat": "Google Gemini (/질문 명령어)",
            "Games": "7 types",
            "Weather": "300+ cities", 
            "Lunch": "200+ menus",
            "Balance": "100 games"
        },
        "endpoints": [
            "/webhook - 카카오톡 봇 엔드포인트",
            "/health - 서버 상태",
            "/ - 홈페이지"
        ]
    })

if __name__ == '__main__':
    # API 키 검증
    try:
        Config.validate_keys()
        logger.info("API 키 검증 완료")
    except ValueError as e:
        logger.error(f"API 키 오류: {e}")
        exit(1)
    
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)