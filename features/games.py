import random
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
import calendar
from config import Config

class GameManager:
    def __init__(self):
        self.word_chain_words = set()
        self.user_scores = defaultdict(int)
        self.daily_attendance = defaultdict(set)
        
        # 단체방 지원을 위한 수정
        self.game_sessions = defaultdict(dict)  # room_id별 세션 관리
        
        self.user_stats = defaultdict(lambda: {
            'total_games': 0,
            'balance_games': 0,
            'number_games': 0,
            'rps_wins': 0,
            'rps_loses': 0,
            'rps_draws': 0,
            'attendance_days': 0,
            '숫자게임_승리': 0,
            '숫자게임_패배': 0,
            '가위바위보_승리': 0,
            '가위바위보_패배': 0,
            '가위바위보_무승부': 0,
            '출석일수': 0
        })
        
        # 방별 데이터 추가
        self.room_data = defaultdict(lambda: {
            'last_balance_game': None,
            'group_votes': defaultdict(list)
        })
        
        # 사주 운세를 위한 사용자 생년월일 저장
        self.user_birth_info = {}
        
        self.balance_games = [
            # 음식 관련
            {"A": "🍕 평생 피자만 먹기", "B": "🍔 평생 햄버거만 먹기"},
            {"A": "🌶️ 평생 매운 음식만 먹기", "B": "🧊 평생 차가운 음식만 먹기"},
            {"A": "🍰 평생 단 것만 먹기", "B": "🧂 평생 짠 것만 먹기"},
            {"A": "🥗 평생 건강식만 먹기", "B": "🍟 평생 정크푸드만 먹기"},
            {"A": "🍜 평생 국물 음식만 먹기", "B": "🍞 평생 마른 음식만 먹기"},
            
            # 능력 관련
            {"A": "✈️ 하늘을 날 수 있지만 걷지 못함", "B": "🏃‍♂️ 엄청 빠르게 달릴 수 있지만 날지 못함"},
            {"A": "🔮 미래를 볼 수 있지만 바꿀 수 없음", "B": "⏰ 과거로 갈 수 있지만 한 번만"},
            {"A": "🧠 천재가 되지만 친구가 없음", "B": "😊 평범하지만 인기가 많음"},
            {"A": "👁️ 투시 능력이 있지만 끌 수 없음", "B": "👂 텔레파시 능력이 있지만 조절 불가"},
            {"A": "💪 힘이 무지막지 강하지만 조절 불가", "B": "🤸 몸이 고무처럼 늘어나지만 아픔"},
            
            # 돈과 시간
            {"A": "💰 돈은 많지만 시간이 없음", "B": "⏰ 시간은 많지만 돈이 없음"},
            {"A": "💳 카드는 무제한이지만 현금 0원", "B": "💵 현금만 무제한이지만 카드 사용 불가"},
            {"A": "🏆 평생 복권 1등이지만 친구 잃음", "B": "🤝 평생 가난하지만 진실한 친구들"},
            {"A": "💎 부자지만 절대 쓸 수 없음", "B": "🆓 가난하지만 모든 게 공짜"},
            {"A": "💸 매일 100만원 벌지만 매일 써야 함", "B": "💰 한 번에 1억 받지만 평생 벌 수 없음"},
            
            # 성격과 감정
            {"A": "🤖 로봇처럼 감정이 없지만 완벽함", "B": "😭 감정이 풍부하지만 실수가 많음"},
            {"A": "😊 항상 행복하지만 현실 인식 불가", "B": "😢 항상 슬프지만 현실을 정확히 봄"},
            {"A": "😡 화를 절대 낼 수 없음", "B": "😨 두려움을 절대 느낄 수 없음"},
            {"A": "🥰 모든 사람을 사랑하지만 사랑받지 못함", "B": "💔 사랑할 수 없지만 모든 사람이 좋아함"},
            {"A": "🎭 감정을 숨길 수 있지만 혼자만 앎", "B": "📢 감정이 다 드러나지만 공감받음"},
            
            # 지식과 소통
            {"A": "📚 모든 지식을 알지만 소통 불가", "B": "💬 소통의 달인이지만 무식함"},
            {"A": "🔤 모든 언어를 알지만 말을 못함", "B": "🗣️ 말은 잘하지만 한 언어만 가능"},
            {"A": "📖 모든 책을 기억하지만 창의력 0", "B": "🎨 창의력 무한이지만 기억력 0"},
            {"A": "🧮 수학 천재지만 다른 건 바보", "B": "🎵 예술 천재지만 논리력 0"},
            {"A": "🔬 과학만 알고 인문학 무지", "B": "📜 인문학만 알고 과학 무지"},
            
            # 생활과 환경
            {"A": "🏠 집에서만 살지만 모든 게 무료", "B": "🌍 어디든 갈 수 있지만 돈이 듦"},
            {"A": "🌞 항상 낮이지만 잠들 수 없음", "B": "🌙 항상 밤이지만 깨어있을 수 없음"},
            {"A": "🥶 항상 춥지만 건강함", "B": "🥵 항상 덥지만 아프지 않음"},
            {"A": "☔ 평생 비가 오는 곳에서 살기", "B": "🌵 평생 사막에서 살기"},
            {"A": "🏔️ 산꼭대기에서만 살 수 있음", "B": "🏖️ 바닷가에서만 살 수 있음"},
            
            # 기술과 미디어
            {"A": "📱 모든 앱이 무료지만 인터넷 1시간/일", "B": "💻 무제한 인터넷이지만 모든 앱 유료"},
            {"A": "📺 TV만 볼 수 있고 핸드폰 금지", "B": "📱 핸드폰만 쓸 수 있고 TV 금지"},
            {"A": "🎮 게임만 할 수 있고 다른 미디어 금지", "B": "📚 책만 읽을 수 있고 전자기기 금지"},
            {"A": "💬 메신저만 가능하고 통화 불가", "B": "📞 통화만 가능하고 메신저 불가"},
            {"A": "📸 사진은 찍을 수 있지만 볼 수 없음", "B": "👀 사진은 볼 수 있지만 찍을 수 없음"},
            
            # 음악과 엔터테인먼트
            {"A": "🎵 평생 같은 노래만 들을 수 있음", "B": "🔇 평생 음악을 들을 수 없음"},
            {"A": "🎤 노래는 잘하지만 춤을 못춤", "B": "💃 춤은 잘추지만 노래를 못함"},
            {"A": "🎬 영화만 볼 수 있고 드라마 금지", "B": "📺 드라마만 볼 수 있고 영화 금지"},
            {"A": "😂 코미디만 볼 수 있음", "B": "😢 슬픈 영화만 볼 수 있음"},
            {"A": "🎪 라이브만 볼 수 있고 영상 금지", "B": "📱 영상만 볼 수 있고 라이브 금지"},
            
            # 외모와 스타일
            {"A": "👗 평생 같은 옷만 입기", "B": "👕 매일 다른 옷이지만 어울리지 않음"},
            {"A": "💇 머리카락이 계속 자라지만 자를 수 없음", "B": "👨‍🦲 머리카락이 영원히 안 자람"},
            {"A": "👥 항상 똑같은 얼굴", "B": "🎭 매일 다른 얼굴로 변함"},
            {"A": "👔 격식 있는 옷만 입을 수 있음", "B": "👕 캐주얼한 옷만 입을 수 있음"},
            {"A": "🌈 무지개색 머리카락", "B": "⚫ 검은색만 입을 수 있음"},
            
            # 인간관계
            {"A": "👥 많은 친구가 있지만 얕은 관계", "B": "👤 친구는 한 명뿐이지만 깊은 관계"},
            {"A": "💑 연애는 잘하지만 결혼 못함", "B": "💒 결혼은 잘하지만 연애 못함"},
            {"A": "👶 아이들만 좋아함", "B": "👴 어른들만 좋아함"},
            {"A": "🗣️ 말은 많이 하지만 경청 못함", "B": "👂 경청은 잘하지만 말을 못함"},
            {"A": "🤝 신뢰는 받지만 사랑받지 못함", "B": "💕 사랑은 받지만 신뢰받지 못함"},
            
            # 직업과 성공
            {"A": "💼 좋아하지 않는 일로 성공", "B": "❤️ 좋아하는 일로 평범하게 살기"},
            {"A": "🏆 1등이지만 혼자 성취", "B": "🤝 2등이지만 팀과 함께 성취"},
            {"A": "💰 돈 많이 버는 지루한 직업", "B": "🎨 돈 적게 버는 재미있는 직업"},
            {"A": "📈 성공했지만 스트레스 많음", "B": "😌 평범하지만 스트레스 없음"},
            {"A": "🌟 유명하지만 사생활 없음", "B": "🔒 무명이지만 자유로운 삶"},
            
            # 건강과 운동
            {"A": "💪 힘은 세지만 지구력 0", "B": "🏃 지구력은 좋지만 힘이 없음"},
            {"A": "🧘 정신건강은 좋지만 몸이 약함", "B": "💪 몸은 건강하지만 정신적으로 불안"},
            {"A": "🥗 건강식만 먹지만 맛없음", "B": "🍰 맛있는 것만 먹지만 건강 악화"},
            {"A": "😴 잠은 많이 자지만 항상 피곤", "B": "☕ 잠은 못 자지만 항상 활기참"},
            {"A": "🚫 병에 안 걸리지만 다칠 수 있음", "B": "🩹 다치지 않지만 병에 걸릴 수 있음"},
            
            # 학습과 교육
            {"A": "📝 시험은 잘 보지만 실무 못함", "B": "💼 실무는 잘하지만 시험 못 봄"},
            {"A": "🎓 공부는 잘하지만 적용 못함", "B": "🔧 적용은 잘하지만 이론 모름"},
            {"A": "📚 암기는 잘하지만 이해 못함", "B": "💡 이해는 잘하지만 기억 못함"},
            {"A": "✏️ 글은 잘 쓰지만 말 못함", "B": "🗣️ 말은 잘하지만 글 못 씀"},
            {"A": "🔢 수학만 잘함", "B": "📖 국어만 잘함"},
            
            # 여행과 모험
            {"A": "✈️ 해외여행만 가능", "B": "🚗 국내여행만 가능"},
            {"A": "🏝️ 휴양지만 갈 수 있음", "B": "🏔️ 산악지대만 갈 수 있음"},
            {"A": "🎒 혼자 여행만 가능", "B": "👥 단체 여행만 가능"},
            {"A": "🚶 걸어서만 여행 가능", "B": "✈️ 비행기로만 이동 가능"},
            {"A": "📷 여행 사진만 찍을 수 있음", "B": "📝 여행 일기만 쓸 수 있음"},
            
            # 취미와 여가
            {"A": "🎨 그림만 그릴 수 있음", "B": "🎵 음악만 들을 수 있음"},
            {"A": "📚 독서만 할 수 있음", "B": "🎮 게임만 할 수 있음"},
            {"A": "🏃 운동만 할 수 있음", "B": "🛋️ 휴식만 할 수 있음"},
            {"A": "🧩 퍼즐만 맞출 수 있음", "B": "🎯 다트만 던질 수 있음"},
            {"A": "🎪 구경만 할 수 있음", "B": "🎭 참여만 할 수 있음"},
            
            # 계절과 날씨
            {"A": "❄️ 겨울만 있는 곳에서 살기", "B": "☀️ 여름만 있는 곳에서 살기"},
            {"A": "🌸 봄만 있는 곳에서 살기", "B": "🍂 가을만 있는 곳에서 살기"},
            {"A": "🌧️ 비 오는 날만 좋아함", "B": "☀️ 맑은 날만 좋아함"},
            {"A": "❄️ 눈 오는 날에만 외출 가능", "B": "🌞 햇빛 나는 날에만 외출 가능"},
            {"A": "🌪️ 바람 부는 날만 활기참", "B": "🌅 고요한 날만 평온함"},
            
            # 교통과 이동
            {"A": "🚗 자동차로만 이동 가능", "B": "🚶 걸어서만 이동 가능"},
            {"A": "🚇 지하철로만 이동 가능", "B": "🚌 버스로만 이동 가능"},
            {"A": "🚲 자전거로만 이동 가능", "B": "🛴 킥보드로만 이동 가능"},
            {"A": "✈️ 비행기로만 장거리 이동", "B": "🚂 기차로만 장거리 이동"},
            {"A": "🏃 빠르게 이동하지만 쉽게 피곤", "B": "🐌 느리게 이동하지만 절대 안 피곤"},
            
            # 미래와 과거
            {"A": "📱 최신 기술만 사용 가능", "B": "📻 옛날 기술만 사용 가능"},
            {"A": "🔮 미래만 생각함", "B": "📜 과거만 생각함"},
            {"A": "⏰ 시간을 앞당길 수 있음", "B": "⏳ 시간을 늦출 수 있음"},
            {"A": "📅 내일만 알 수 있음", "B": "📆 어제만 기억할 수 있음"},
            {"A": "🚀 미래로만 갈 수 있음", "B": "🏛️ 과거로만 갈 수 있음"},
            
            # 감각과 인지
            {"A": "👀 시각만 뛰어남", "B": "👂 청각만 뛰어남"},
            {"A": "👃 후각만 뛰어남", "B": "👅 미각만 뛰어남"},
            {"A": "✋ 촉각만 뛰어남", "B": "🧠 직감만 뛰어남"},
            {"A": "🎨 색깔을 잘 구분함", "B": "🔊 소리를 잘 구분함"},
            {"A": "👁️ 멀리는 잘 보지만 가까이 못 봄", "B": "🔍 가까이는 잘 보지만 멀리 못 봄"},
            
            # 마지막 특별한 것들
            {"A": "🎭 연기는 잘하지만 진실을 말할 수 없음", "B": "💯 진실만 말하지만 연기를 못함"},
            {"A": "🎲 운이 매우 좋지만 노력 효과 없음", "B": "💪 노력한 만큼 성과가 나지만 운이 없음"},
            {"A": "🔄 실수를 되돌릴 수 있지만 성공도 되돌려짐", "B": "⚡ 한 번의 기회만 있지만 확실한 성공"},
            {"A": "👑 왕이 되지만 책임이 무거움", "B": "🆓 자유롭지만 영향력이 없음"},
            {"A": "🌟 영원히 살지만 사랑하는 사람들은 떠남", "B": "⏰ 짧게 살지만 모든 순간이 의미있음"}
        ]
    
    def get_session_key(self, user_id, room_id, game_type="default"):
        """고유 세션 키 생성"""
        return f"{room_id}_{user_id}_{game_type}"
    
    # 기존 메서드들...
    def balance_game(self):
        """밸런스 게임"""
        game = random.choice(self.balance_games)
        return f"⚖️ **밸런스 게임!**\n\n1️⃣ {game['A']}\n\n🆚\n\n2️⃣ {game['B']}\n\n둘 중 뭘 선택할래? (1 또는 2로 답변)\n💡 이유도 함께 말해주면 더 재미있어요!"
    
    def balance_game_with_voting(self, room_id):
        """단체방용 밸런스 게임 (투표 기능)"""
        game = random.choice(self.balance_games)
        self.room_data[room_id]['last_balance_game'] = game
        self.room_data[room_id]['group_votes'] = defaultdict(list)
        
        group_notice = ""
        if room_id != 'private':
            group_notice = "\n\n👥 **단체방 모드**: 모두 1 또는 2로 투표해보세요!\n결과는 '/게임 투표결과'로 확인!"
        
        return f"⚖️ **밸런스 게임!**\n\n1️⃣ {game['A']}\n\n🆚\n\n2️⃣ {game['B']}\n\n둘 중 뭘 선택할래? (1 또는 2로 답변)\n💡 이유도 함께 말해주면 더 재미있어요!{group_notice}"
    
    def vote_balance(self, user_id, room_id, choice):
        """밸런스 게임 투표"""
        if choice == '1':
            choice_internal = 'A'
            choice_display = '1'
        elif choice == '2':
            choice_internal = 'B'
            choice_display = '2'
        else:
            return "1 또는 2로 투표해주세요!"
        
        if room_id == 'private':
            return "개인 메시지에서는 투표 기능을 사용할 수 없어요!"
        
        user_votes = self.room_data[room_id]['group_votes']
        for vote_choice in ['A', 'B']:
            if user_id in user_votes[vote_choice]:
                user_votes[vote_choice].remove(user_id)
        
        user_votes[choice_internal].append(user_id)
        
        return f"✅ **{choice_display}번**에 투표하셨습니다!\n'/게임 투표결과'로 현재 결과를 확인해보세요!"
    
    def get_voting_result(self, room_id):
        """투표 결과 확인"""
        if room_id == 'private':
            return "개인 메시지에서는 투표 결과를 확인할 수 없어요!"
        
        game = self.room_data[room_id]['last_balance_game']
        if not game:
            return "진행 중인 밸런스 게임이 없습니다!"
        
        votes = self.room_data[room_id]['group_votes']
        a_count = len(votes['A'])
        b_count = len(votes['B'])
        total = a_count + b_count
        
        if total == 0:
            return "아직 투표한 사람이 없어요! 1 또는 2로 투표해주세요!"
        
        a_percent = (a_count / total) * 100
        b_percent = (b_count / total) * 100
        
        winner = "1️⃣번" if a_count > b_count else "2️⃣번" if b_count > a_count else "🤝 무승부"
        
        return f"""📊 **투표 결과**
1️⃣ **1번**: {game['A']}
👥 {a_count}명 ({a_percent:.1f}%)
2️⃣ **2번**: {game['B']}  
👥 {b_count}명 ({b_percent:.1f}%)
🏆 **결과**: {winner}
📈 총 {total}명 참여"""

    def lunch_recommendation(self, room_id=None):
        """점심 추천 (바로 추천)"""
        lunch_menus = [
            # 한식
            "🍖 삼겹살", "🍜 라면", "🍱 도시락", "🥘 찌개", "🍲 국밥",
            "🍳 계란볶음밥", "🥟 만두", "🍖 갈비", "🐟 생선구이", "🍄 버섯볶음",
            "🍚 비빔밥", "🍜 냉면", "🍛 김치볶음밥", "🥩 불고기", "🍲 삼계탕",
            "🍜 짜장면", "🍝 짬뽕", "🥟 물만두", "🍳 김치찌개", "🍲 된장찌개",
            "🐟 고등어구이", "🍖 족발", "🍲 순두부찌개", "🍜 칼국수", "🍱 김밥",
            "🍳 제육볶음", "🥘 부대찌개", "🍲 감자탕", "🐟 생선찌개", "🍜 우동",
            
            # 국밥 특집 (10개)
            "🍲 돼지국밥", "🐄 소머리국밥", "🐟 해장국", "🦐 새우국밥", "🐙 낙지국밥",
            "🥩 설렁탕", "🦴 갈비탕", "🍲 콩나물국밥", "🐟 북어국", "🍲 순대국밥",
            
            # 경남지방 음식 (10개)
            "🐟 진주냉면", "🍱 진주비빔밥", "🦀 간장게장", "🐟 밀면", "🍜 육개장",
            "🐟 조개국밥", "🦐 멸치국수", "🐟 아구찜", "🦀 꽃게탕", "🍲 곰장어탕",
            
            # 지역 특산물 (30개)
            "🦐 낙곱새", "🐟 회냉면", "🍜 물회", "🐙 산낙지", "🦀 꽃게백숙",
            "🐟 고등어회", "🦑 오징어순대", "🐚 굴국밥", "🐟 대구탕", "🦐 새우장",
            "🍜 함흥냉면", "🍲 평양냉면", "🥟 개성만두", "🍜 온면", "🍲 추어탕",
            "🐟 민물매운탕", "🦆 오리백숙", "🐓 닭한마리", "🐷 순대국", "🍲 뼈해장국",
            "🐟 생선구이정식", "🦀 간장새우", "🐙 쭈꾸미볶음", "🦑 오징어볶음", "🐚 조개찜",
            "🍜 잔치국수", "🥟 왕만두", "🍲 갈치조림", "🐟 고등어조림", "🦐 새우볶음밥",
            
            # 중식
            "🍜 짜장면", "🍝 짬뽕", "🥟 탕수육", "🍛 볶음밥", "🥢 깐풍기",
            "🦐 새우볶음밥", "🍖 양장피", "🥟 군만두", "🍲 마파두부", "🍜 간짜장",
            "🥘 유린기", "🍛 계란볶음밥", "🦑 오징어볶음", "🍖 팔보채", "🥟 물만두",
            
            # 일식
            "🍣 초밥", "🍜 우동", "🍱 덮밥", "🐟 회", "🍤 돈카츠",
            "🍜 라멘", "🍱 규동", "🍤 새우튀김", "🐟 연어덮밥", "🍜 소바",
            "🍱 치라시", "🍤 가츠동", "🐟 장어덮밥", "🍜 츠케멘", "🍱 오야코동",
            
            # 양식
            "🍕 피자", "🍔 햄버거", "🍝 스파게티", "🥗 샐러드", "🥪 샌드위치",
            "🍖 스테이크", "🍗 치킨", "🌭 핫도그", "🧀 치즈버거", "🥙 랩",
            "🍝 파스타", "🥩 립", "🍖 바베큐", "🥗 시저샐러드", "🍞 브런치",
            "🍝 크림파스타", "🍖 폭립", "🥘 리조또", "🍗 윙", "🥪 클럽샌드위치",
            
            # 분식
            "🌭 떡볶이", "🥟 순대", "🍳 김밥", "🥞 호떡", "🍢 어묵",
            "🌮 타코야키", "🥘 쫄면", "🍳 계란빵", "🥟 튀김", "🌭 핫바",
            "🍜 라볶이", "🥘 비빔국수", "🍳 토스트", "🥞 붕어빵", "🍢 꼬치",
            
            # 치킨 특집
            "🍗 후라이드치킨", "🍗 양념치킨", "🍗 간장치킨", "🍗 마늘치킨", "🍗 허니치킨",
            "🍗 불닭치킨", "🍗 치킨무", "🍗 닭강정", "🍗 치킨텐더", "🍗 윙봉",
            "🍗 치킨버거", "🍗 반반치킨", "🍗 순살치킨", "🍗 뿌링클", "🍗 치킨샐러드",
            
            # 피자 특집
            "🍕 페퍼로니피자", "🍕 치즈피자", "🍕 콤비네이션피자", "🍕 불고기피자", "🍕 하와이안피자",
            "🍕 마르게리타", "🍕 고구마피자", "🍕 시카고피자", "🍕 씬피자", "🍕 도우피자",
            
            # 면 요리 특집
            "🍜 물냉면", "🍜 비빔냉면", "🍜 온면", "🍜 막국수", "🍜 메밀국수",
            "🍝 알리오올리오", "🍝 까르보나라", "🍝 아라비아따", "🍝 봉골레", "🍝 페스토",
            "🍜 쌀국수", "🍜 팟타이", "🍜 볶음우동", "🍜 야끼소바", "🍜 비빔국수",
            
            # 아시안 퓨전
            "🌮 타코", "🥙 케밥", "🍛 카레", "🥘 파에야", "🍲 똠양꿍",
            "🍜 쌀국수", "🥟 딤섬", "🍖 바베큐", "🥗 그릭샐러드", "🍞 브리또",
            "🌯 파히타", "🥙 샤와마", "🍛 인도카레", "🍜 라멘", "🥘 파스타",
            
            # 디저트&음료
            "🍰 케이크", "🍦 아이스크림", "🧁 컵케이크", "🍪 쿠키", "🍩 도넛",
            "☕ 커피", "🧋 버블티", "🥤 음료수", "🍵 차", "🥛 밀크셰이크",
            
            # 건강식
            "🥗 그린샐러드", "🥤 스무디", "🍎 과일", "🥑 아보카도토스트", "🥙 베지랩",
            "🍲 두부요리", "🥘 현미밥", "🍵 차", "🥛 요거트", "🍇 과일샐러드",
            
            # 야식
            "🍗 치킨", "🍕 피자", "🌭 떡볶이", "🍜 라면", "🥟 만두",
            "🍖 족발", "🦐 새우튀김", "🍢 꼬치", "🥘 쫄면", "🍳 계란말이",
            
            # 든든한 한끼
            "🍱 정식", "🍲 찌개+밥", "🍜 국밥", "🥘 덮밥", "🍛 볶음밥",
            "🍖 고기+밥", "🐟 생선+밥", "🍲 탕+밥", "🥟 만두+밥", "🍳 계란+밥"
        ]
        
        selected = random.choice(lunch_menus)
        
        comments = [
            "오늘 딱 좋은 선택이에요!", "맛있게 드세요!", "좋은 선택입니다!",
            "오늘 기분에 딱 맞는 메뉴네요!", "든든하게 드세요!", "맛있는 점심 되세요!",
            "완벽한 선택이에요!", "오늘은 이걸로 결정!", "행복한 식사 시간 되세요!",
            "이거 어때요?", "추천드려요!", "오늘의 베스트 선택!", 
            "맛있을 것 같아요!", "좋은 하루 되세요!", "든든한 한 끼!"
        ]
        comment = random.choice(comments)
        
        # 시간대별 인사말
        current_hour = datetime.now().hour
        if 11 <= current_hour < 14:
            time_msg = "점심시간이네요! "
        elif 14 <= current_hour < 17:
            time_msg = "늦은 점심이지만 "
        else:
            time_msg = ""
        
        # 단체방 여부 확인
        group_msg = "🏢 단체방 추천: " if room_id and room_id != 'private' else ""
        
        return f"🍽️ **{group_msg}오늘의 점심 추천**\n\n🎯 **{selected}**\n\n💬 {time_msg}{comment}"

    def number_guessing(self, user_id, room_id, guess=None):
        """업앤다운 (방별 구분)"""
        session_key = self.get_session_key(user_id, room_id, "number")
        
        if session_key not in self.game_sessions:
            # 새 게임 시작
            self.game_sessions[session_key] = {
                'answer': random.randint(1, 100),
                'attempts': 0,
                'max_attempts': 7,
                'start_time': time.time()
            }
            
            # 단체방인 경우 주의사항 추가
            group_notice = ""
            if room_id != 'private':
                group_notice = "\n⚠️ 단체방에서는 다른 사람이 답을 볼 수 있어요!"
            
            return f"🔢 **숫자 맞히기 게임!**\n\n🎯 1부터 100 사이의 숫자를 맞춰보세요!\n⏰ 기회는 7번입니다.\n\n숫자를 입력해주세요!{group_notice}"
        
        if guess is None:
            session = self.game_sessions[session_key]
            remaining = session['max_attempts'] - session['attempts']
            return f"숫자를 입력해주세요! (1-100)\n남은 기회: {remaining}번"
        
        try:
            guess = int(guess)
            if guess < 1 or guess > 100:
                return "1부터 100 사이의 숫자를 입력해주세요!"
        except ValueError:
            return "올바른 숫자를 입력해주세요!"
        
        session = self.game_sessions[session_key]
        session['attempts'] += 1
        answer = session['answer']
        
        if guess == answer:
            attempts = session['attempts']
            time_taken = time.time() - session['start_time']
            score = max(15 - attempts * 2, 3)
            
            self.user_scores[f"{room_id}_{user_id}"] += score
            self.user_stats[f"{room_id}_{user_id}"]['숫자게임_승리'] += 1
            del self.game_sessions[session_key]
            
            return f"🎉 **정답입니다!**\n\n🎯 답: {answer}\n🎮 시도: {attempts}번\n⏰ 시간: {time_taken:.1f}초\n🏆 점수: +{score}점\n\n'/게임 숫자'로 새 게임 시작!"
        
        remaining = session['max_attempts'] - session['attempts']
        
        if remaining <= 0:
            self.user_stats[f"{room_id}_{user_id}"]['숫자게임_패배'] += 1
            del self.game_sessions[session_key]
            return f"😅 **게임 오버!**\n\n🎯 정답: {answer}\n🎮 총 시도: {session['max_attempts']}번\n\n'/게임 숫자'로 다시 도전!"
        
        # 힌트 개선
        diff = abs(guess - answer)
        if diff <= 5:
            hint_level = "🔥 매우 가까워요!"
        elif diff <= 15:
            hint_level = "🌡️ 가까워요!"
        elif diff <= 30:
            hint_level = "😐 보통이에요"
        else:
            hint_level = "🥶 멀어요"
        
        direction = "📈 UP! 더 큰 숫자" if guess < answer else "📉 DOWN! 더 작은 숫자"
        
        return f"{direction}\n{hint_level}\n\n남은 기회: {remaining}번"

    def rps_game(self, user_id, user_choice):
        """가위바위보 게임"""
        choices = ["가위", "바위", "보"]
        emojis = {"가위": "✂️", "바위": "🪨", "보": "📄"}
        
        if user_choice not in choices:
            return "🎮 **가위바위보**\n\n가위, 바위, 보 중 하나를 선택해주세요!\n예: `/게임 가위바위보 가위`"
        
        bot_choice = random.choice(choices)
        
        user_emoji = emojis[user_choice]
        bot_emoji = emojis[bot_choice]
        
        result_msg = f"🎮 **가위바위보!**\n\n👤 당신: {user_emoji} {user_choice}\n🤖 봇: {bot_emoji} {bot_choice}\n\n"
        
        if user_choice == bot_choice:
            self.user_stats[user_id]['가위바위보_무승부'] += 1
            return result_msg + "🤝 무승부입니다!"
        elif (user_choice == "가위" and bot_choice == "보") or \
             (user_choice == "바위" and bot_choice == "가위") or \
             (user_choice == "보" and bot_choice == "바위"):
            self.user_scores[user_id] += 3
            self.user_stats[user_id]['가위바위보_승리'] += 1
            return result_msg + "🎉 **당신의 승리!** +3점"
        else:
            self.user_stats[user_id]['가위바위보_패배'] += 1
            return result_msg + "😅 **봇의 승리!** 다시 도전해보세요!"

    def daily_attendance(self, user_id):
        """일일 출석체크"""
        today = datetime.now().date()
        
        if today in self.daily_attendance[user_id]:
            consecutive = self.get_consecutive_days(user_id)
            total_days = len(self.daily_attendance[user_id])
            return f"✅ **오늘은 이미 출석하셨습니다!**\n\n📅 연속 출석: {consecutive}일\n📊 총 출석: {total_days}일\n🌙 내일 다시 만나요!"
        
        self.daily_attendance[user_id].add(today)
        
        # 연속 출석 보너스
        consecutive = self.get_consecutive_days(user_id)
        base_points = random.randint(3, 8)
        bonus = min(consecutive // 7, 10)  # 주간 보너스 (최대 10점)
        total_points = base_points + bonus
        
        self.user_scores[user_id] += total_points
        self.user_stats[user_id]['출석일수'] += 1
        
        bonus_msg = f"\n🎁 연속 보너스: +{bonus}점" if bonus > 0 else ""
        
        return f"📅 **출석체크 완료!**\n\n🎁 기본 포인트: +{base_points}점{bonus_msg}\n💯 총 획득: +{total_points}점\n\n📊 연속 출석: {consecutive}일\n📈 총 출석: {len(self.daily_attendance[user_id])}일\n\n🔥 연속 출석하면 보너스가 더 커져요!"

    def get_consecutive_days(self, user_id):
        """연속 출석일 계산"""
        if not self.daily_attendance[user_id]:
            return 0
        
        dates = sorted(self.daily_attendance[user_id], reverse=True)
        consecutive = 1
        
        for i in range(1, len(dates)):
            if dates[i-1] - dates[i] == timedelta(days=1):
                consecutive += 1
            else:
                break
        
        return consecutive

    # ============ 사주 운세 시스템 (이식) ============
    def fortune_telling(self, user_id, birth_info=None):
        """사주 기반 오늘의 운세"""
        # 생년월일 정보가 없으면 입력 요청
        if not birth_info:
            return self.request_birth_info()
        
        try:
            # 생년월일 파싱
            birth_year, birth_month, birth_day = map(int, birth_info.split('-'))
            
            # 사주 오행 계산
            birth_elements = self.calculate_birth_elements(birth_year, birth_month, birth_day)
            
            # 오늘 날짜의 오행
            today = datetime.now()
            today_elements = self.calculate_daily_elements(today.year, today.month, today.day)
            
            # 오행 상성 분석
            compatibility = self.analyze_five_elements_compatibility(birth_elements, today_elements)
            
            # 운세 생성
            fortune_result = self.generate_sajupalja_fortune(birth_elements, today_elements, compatibility)
            
            return fortune_result
            
        except ValueError:
            return "❌ 생년월일 형식이 올바르지 않습니다.\n올바른 형식: YYYY-MM-DD\n예시: 1990-03-15"

    def request_birth_info(self):
        """생년월일 입력 요청"""
        return """🔮 **사주 기반 오늘의 운세**

📅 정확한 운세를 위해 생년월일을 알려주세요!

**입력 방법:**
`/게임 운세 YYYY-MM-DD`

**예시:**
• `/게임 운세 1990-03-15`
• `/게임 운세 1985-12-07`
• `/게임 운세 2000-06-23`

🌟 한번 입력하시면 다음부터는 간단히 `/게임 운세`만 입력하셔도 됩니다!"""

    def calculate_birth_elements(self, year, month, day):
        """태어난 년월일의 오행 계산"""
        # 천간 (10개) - 년도 계산
        heavenly_stems = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
        stem_elements = ["목", "목", "화", "화", "토", "토", "금", "금", "수", "수"]
        
        # 지지 (12개) - 년도 계산  
        earthly_branches = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
        branch_elements = ["수", "토", "목", "목", "토", "화", "화", "토", "금", "금", "토", "수"]
        
        # 년주 계산 (1984년 = 갑자 기준)
        year_stem_idx = (year - 4) % 10
        year_branch_idx = (year - 4) % 12
        
        # 월주 계산 (복잡한 계산을 단순화)
        month_stem_idx = (year_stem_idx * 2 + month) % 10
        month_branch_idx = (month - 1) % 12
        
        # 일주 계산 (1900년 1월 1일 기준으로 계산)
        days_since_1900 = self.calculate_days_since_1900(year, month, day)
        day_stem_idx = (days_since_1900 + 4) % 10  # 1900년 1월 1일이 갑자
        day_branch_idx = (days_since_1900 + 4) % 12
        
        return {
            "년주": {
                "천간": heavenly_stems[year_stem_idx],
                "지지": earthly_branches[year_branch_idx],
                "오행": stem_elements[year_stem_idx]
            },
            "월주": {
                "천간": heavenly_stems[month_stem_idx],
                "지지": earthly_branches[month_branch_idx],
                "오행": stem_elements[month_stem_idx]
            },
            "일주": {
                "천간": heavenly_stems[day_stem_idx],
                "지지": earthly_branches[day_branch_idx],
                "오행": stem_elements[day_stem_idx]
            },
            "주요오행": stem_elements[day_stem_idx]  # 일간이 가장 중요
        }

    def calculate_days_since_1900(self, year, month, day):
        """1900년 1월 1일부터 며칠이 지났는지 계산"""
        target_date = datetime(year, month, day)
        base_date = datetime(1900, 1, 1)
        return (target_date - base_date).days

    def calculate_daily_elements(self, year, month, day):
        """오늘 날짜의 오행 계산"""
        return self.calculate_birth_elements(year, month, day)

    def analyze_five_elements_compatibility(self, birth_elements, today_elements):
        """오행 상성 분석"""
        # 오행 상생/상극 관계
        element_relations = {
            "목": {"생": "화", "극": "토", "생받는": "수", "극받는": "금"},
            "화": {"생": "토", "극": "금", "생받는": "목", "극받는": "수"},
            "토": {"생": "금", "극": "수", "생받는": "화", "극받는": "목"},
            "금": {"생": "수", "극": "목", "생받는": "토", "극받는": "화"},
            "수": {"생": "목", "극": "화", "생받는": "금", "극받는": "토"}
        }
        
        birth_main = birth_elements["주요오행"]
        today_main = today_elements["주요오행"]
        
        relations = element_relations[birth_main]
        
        if today_main == birth_main:
            return {"type": "동일", "power": 50, "desc": "평온한"}
        elif today_main == relations["생"]:
            return {"type": "상생", "power": 80, "desc": "매우 좋은"}
        elif today_main == relations["생받는"]:
            return {"type": "생받음", "power": 70, "desc": "좋은"}
        elif today_main == relations["극"]:
            return {"type": "상극", "power": 20, "desc": "주의가 필요한"}
        elif today_main == relations["극받는"]:
            return {"type": "극받음", "power": 30, "desc": "조심스러운"}
        else:
            return {"type": "중성", "power": 50, "desc": "보통의"}

    def generate_sajupalja_fortune(self, birth_elements, today_elements, compatibility):
        """사주팔자 기반 운세 생성"""
        birth_main = birth_elements["주요오행"]
        today_main = today_elements["주요오행"]
        relation_type = compatibility["type"]
        power = compatibility["power"]
        
        # 오행별 성격과 특징
        element_traits = {
            "목": {"성격": "성장하고 발전하려는", "색깔": "초록색", "방향": "동쪽", "시간": "아침", "계절": "봄"},
            "화": {"성격": "열정적이고 활동적인", "색깔": "빨간색", "방향": "남쪽", "시간": "정오", "계절": "여름"},
            "토": {"성격": "안정적이고 신중한", "색깔": "노란색", "방향": "중앙", "시간": "오후", "계절": "늦여름"},
            "금": {"성격": "의지가 강하고 결단력 있는", "색깔": "하얀색", "방향": "서쪽", "시간": "저녁", "계절": "가을"},
            "수": {"성격": "지혜롭고 유연한", "색깔": "검은색", "방향": "북쪽", "시간": "밤", "계절": "겨울"}
        }
        
        # 상성별 메시지
        compatibility_messages = {
            "상생": [
                "오늘은 당신의 에너지가 증폭되는 날입니다!",
                "계획했던 일들이 순조롭게 풀릴 것입니다.",
                "새로운 기회가 찾아올 가능성이 높습니다.",
                "타인과의 협력에서 좋은 결과를 얻을 수 있습니다."
            ],
            "생받음": [
                "외부로부터 도움을 받기 좋은 날입니다.",
                "멘토나 선배의 조언을 구해보세요.",
                "학습이나 새로운 정보 습득에 유리합니다.",
                "인맥을 통한 기회가 생길 수 있습니다."
            ],
            "동일": [
                "내면의 힘이 안정된 하루입니다.",
                "자신만의 페이스로 일을 진행하세요.",
                "혼자만의 시간을 갖는 것이 도움됩니다.",
                "평소 하던 일에 집중하기 좋은 날입니다."
            ],
            "상극": [
                "도전적인 일이 있을 수 있지만 극복 가능합니다.",
                "감정 조절에 신경 쓰세요.",
                "중요한 결정은 신중하게 내리세요.",
                "스트레스 관리가 중요한 하루입니다."
            ],
            "극받음": [
                "에너지 소모가 클 수 있으니 무리하지 마세요.",
                "건강 관리에 특히 신경 쓰세요.",
                "휴식을 충분히 취하는 것이 좋습니다.",
                "중요한 일은 내일로 미루는 것을 고려해보세요."
            ],
            "중성": [
                "평범하지만 안정적인 하루가 될 것입니다.",
                "꾸준함이 빛을 발하는 날입니다.",
                "작은 일부터 차근차근 처리해보세요.",
                "주변 상황을 잘 관찰하는 것이 도움됩니다."
            ]
        }
        
        # 운세 등급 결정
        if power >= 80:
            grade = "대길"
            emoji = "✨"
        elif power >= 70:
            grade = "길"
            emoji = "🌟"
        elif power >= 60:
            grade = "소길"
            emoji = "🍀"
        elif power >= 40:
            grade = "평"
            emoji = "😐"
        elif power >= 30:
            grade = "소주의"
            emoji = "⚠️"
        else:
            grade = "주의"
            emoji = "🚨"
        
        # 메시지 선택
        main_message = random.choice(compatibility_messages[relation_type])
        
        # 오행별 조언
        birth_trait = element_traits[birth_main]
        today_trait = element_traits[today_main]
        
        advice_list = [
            f"{birth_trait['색깔']}을 활용해보세요",
            f"{birth_trait['방향']} 방향으로 나가보세요",
            f"{birth_trait['시간']} 시간대가 특히 좋습니다",
            f"{today_trait['계절']}의 기운을 느껴보세요",
            "깊은 숨을 쉬며 마음을 진정시키세요",
            "감사한 마음을 가져보세요",
            "자연과 가까운 곳에서 시간을 보내세요"
        ]
        advice = random.choice(advice_list)
        
        # 행운의 숫자 (오행 기반)
        element_numbers = {
            "목": [1, 2, 11, 12, 21, 22],
            "화": [3, 4, 13, 14, 23, 24],
            "토": [5, 6, 15, 16, 25, 26],
            "금": [7, 8, 17, 18, 27, 28],
            "수": [9, 10, 19, 20, 29, 30]
        }
        
        lucky_numbers = sorted(random.sample(element_numbers[birth_main], 3) +
                              random.sample(element_numbers[today_main], 3))
        
        return f"""🔮 **사주 기반 오늘의 운세**

👤 **당신의 사주**: {birth_elements['년주']['천간']}{birth_elements['년주']['지지']}년 {birth_elements['월주']['천간']}{birth_elements['월주']['지지']}월 {birth_elements['일주']['천간']}{birth_elements['일주']['지지']}일
🌟 **주요 오행**: {birth_main}({birth_trait['성격']} 성향)
📅 **오늘의 오행**: {today_main}

{emoji} **오늘의 운세**: {grade}
🔗 **오행 관계**: {relation_type} ({compatibility['desc']} 기운)

💫 {main_message}

🎲 **행운의 숫자**: {', '.join(map(str, lucky_numbers))}
🌈 **행운의 색**: {birth_trait['색깔']}, {today_trait['색깔']}
⏰ **좋은 시간**: {birth_trait['시간']} ~ {today_trait['시간']}
🧭 **좋은 방향**: {birth_trait['방향']}
💝 **오늘의 조언**: {advice}

✨ 오행의 조화로 하루를 보내세요!"""

    def get_user_score(self, user_id):
        """사용자 점수 조회"""
        score = self.user_scores[user_id]
        rank_info = self.get_user_rank(user_id)
        stats = self.user_stats[user_id]
        
        stats_msg = ""
        if stats:
            stats_msg = "\n📈 **게임 통계**\n"
            for game, count in stats.items():
                if count > 0:
                    stats_msg += f"• {game.replace('_', ' ')}: {count}회\n"
        
        # 사용자 이름 표시 개선
        display_name = user_id.split('_')[-1] if '_' in user_id else user_id
        
        return f"📊 **{display_name}님의 게임 현황**\n\n🏆 총 점수: {score}점\n🎖️ 순위: {rank_info}{stats_msg}\n💡 더 많은 게임에 참여해서 점수를 올려보세요!"

    def get_user_rank(self, user_id):
        """사용자 순위 계산"""
        if not self.user_scores:
            return "순위 없음"
            
        sorted_scores = sorted(self.user_scores.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (uid, score) in enumerate(sorted_scores, 1):
            if uid == user_id:
                total_users = len(sorted_scores)
                return f"{rank}위 / {total_users}명"
        return "순위 외"

    def get_leaderboard(self, room_id=None):
        """리더보드 (방별 구분)"""
        if not self.user_scores:
            return "🎮 **게임 리더보드**\n\n아직 게임에 참여한 사용자가 없습니다!\n게임을 시작해서 1등을 차지해보세요! 🏆"
        
        # 방별 필터링 (room_id가 있는 경우)
        if room_id and room_id != 'private':
            room_scores = {k: v for k, v in self.user_scores.items() if k.startswith(f"{room_id}_")}
            if not room_scores:
                return f"🎮 **이 방 리더보드**\n\n이 방에서 게임에 참여한 사용자가 없습니다!"
            sorted_scores = sorted(room_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            title = f"🏆 **이 방 리더보드** (TOP 10)"
        else:
            sorted_scores = sorted(self.user_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            title = "🏆 **전체 리더보드** (TOP 10)"
        
        leaderboard = f"{title}\n\n"
        medals = ["🥇", "🥈", "🥉"]
        
        for rank, (user_id, score) in enumerate(sorted_scores, 1):
            medal = medals[rank-1] if rank <= 3 else f"🏅 {rank}위"
            # 사용자 이름 익명화
            if '_' in user_id:  # room_id_user_id 형태
                display_name = user_id.split('_')[-1][-3:] if len(user_id.split('_')[-1]) > 3 else user_id.split('_')[-1]
            else:
                display_name = user_id[-3:] if len(user_id) > 3 else user_id
            leaderboard += f"{medal} User-{display_name}: {score}점\n"
        
        total_players = len(sorted_scores)
        leaderboard += f"\n📊 총 참여자: {total_players}명"
        
        return leaderboard

    def parse_game_command(self, user_id, room_id, command_parts):
        """게임 명령어 파싱 및 실행 (방별 구분)"""
        if len(command_parts) < 2:
            return self.show_game_menu(room_id)
        
        game_type = command_parts[1].lower()
        
        # 숫자 게임 답변 확인 (우선순위)
        number_key = self.get_session_key(user_id, room_id, "number")
        if number_key in self.game_sessions and game_type.isdigit():
            return self.number_guessing(user_id, room_id, game_type)
        
        # 투표 처리 (단체방 전용) - 1,2로 변경
        if game_type in ['1', '2'] and room_id != 'private':
            return self.vote_balance(user_id, room_id, game_type)
        
        # 게임별 처리
        if game_type in ["밸런스", "balance"]:
            if room_id != 'private':
                return self.balance_game_with_voting(room_id)
            else:
                return self.balance_game()
        
        elif game_type in ["숫자", "number", "num"]:
            guess = command_parts[2] if len(command_parts) > 2 else None
            return self.number_guessing(user_id, room_id, guess)
        
        elif game_type in ["가위바위보", "가바보", "rps"]:
            choice = command_parts[2] if len(command_parts) > 2 else ""
            return self.rps_game(f"{room_id}_{user_id}", choice)
        
        elif game_type in ["출석", "attendance", "체크"]:
            return self.daily_attendance(f"{room_id}_{user_id}")
        
        elif game_type in ["운세", "fortune", "luck"]:
            if len(command_parts) >= 3:
                # 생년월일이 함께 입력된 경우
                birth_info = command_parts[2]
                # 사용자별 생년월일 저장
                self.user_birth_info[f"{room_id}_{user_id}"] = birth_info
                return self.fortune_telling(f"{room_id}_{user_id}", birth_info)
            elif f"{room_id}_{user_id}" in self.user_birth_info:
                # 이미 저장된 생년월일 사용
                return self.fortune_telling(f"{room_id}_{user_id}", self.user_birth_info[f"{room_id}_{user_id}"])
            else:
                # 생년월일 입력 요청
                return self.fortune_telling(f"{room_id}_{user_id}")
        
        elif game_type in ["점수", "score", "내점수"]:
            return self.get_user_score(f"{room_id}_{user_id}")
        
        elif game_type in ["랭킹", "ranking", "순위"]:
            return self.get_leaderboard(room_id)
        
        elif game_type in ["투표결과", "결과"]:
            return self.get_voting_result(room_id)
        
        else:
            return f"'{game_type}' 게임을 찾을 수 없습니다.\n\n{self.show_game_menu(room_id)}"

    def show_game_menu(self, room_id=None):
        """게임 메뉴 표시 (방별 구분)"""
        group_features = ""
        if room_id and room_id != 'private':
            group_features = """
👥 **단체방 전용**
• `/게임 밸런스` - 투표형 밸런스 게임
• `/게임 투표결과` - 현재 투표 결과 확인
• 1 또는 2 - 밸런스 게임 투표
"""
        
        return f"""🎮 **게임 센터에 오신 것을 환영합니다!**

🎯 **미니게임**
• `/게임 밸런스` - 선택의 순간! 밸런스 게임 (100가지)
• `/게임 가위바위보 [가위/바위/보]` - 전통 게임

🧠 **두뇌게임**  
• `/게임 숫자` - 숫자 맞히기 (1-100)

🎊 **일일 컨텐츠**
• `/게임 출석` - 매일 출석하고 포인트 받기
• `/게임 운세 [YYYY-MM-DD]` - 사주 기반 개인 맞춤 운세
  예: `/게임 운세 1990-03-15`

📊 **랭킹 & 통계**
• `/게임 점수` - 내 점수와 통계 확인  
• `/게임 랭킹` - 전체 순위 보기{group_features}

🎁 **팁**: 
• 연속 출석하면 보너스 포인트가 더 많아져요!
• 생년월일 등록하면 매일 개인 맞춤 사주 운세를 받을 수 있어요!

재미있는 게임을 선택해보세요! 🌟"""