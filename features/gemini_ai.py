import google.generativeai as genai
from config import Config 
import logging
from collections import defaultdict
from datetime import datetime

print("GeminiAI 모듈 로딩 중...")

# Gemini API 설정
genai.configure(api_key=Config.GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config=Config.GENERATION_CONFIG
)

print("Gemini API 설정 완료")

# 대화 기록 저장
conversations = defaultdict(list)

class GeminiAI:
    @staticmethod
    def save_conversation(user_id, user_message, ai_response):
        """대화 기록 저장"""
        conversations[user_id].append({
            'user': user_message,
            'ai': ai_response,
            'timestamp': datetime.now()
        })
        
        # 최근 5개 대화만 유지
        if len(conversations[user_id]) > 5:
            conversations[user_id] = conversations[user_id][-5:]

    @staticmethod
    def build_context_message(user_id, current_message):
        """컨텍스트가 포함된 메시지 생성"""
        history = conversations.get(user_id, [])
        context_message = Config.SYSTEM_PROMPT + "\n\n"
        
        # 최근 3개 대화 포함
        recent_history = history[-3:] if len(history) > 3 else history
        
        if recent_history:
            context_message += "최근 대화 내역:\n"
            for conv in recent_history:
                context_message += f"사용자: {conv['user']}\n"
                context_message += f"AI: {conv['ai']}\n\n"
        
        context_message += f"현재 질문: {current_message}"
        return context_message

    @staticmethod
    def get_response(user_message, user_id):
        """Gemini AI 응답 생성 - 백그라운드용"""
        try:
            logging.info(f"백그라운드 AI 처리: {user_message}")
            
            # 컨텍스트가 포함된 메시지 생성
            context_message = GeminiAI.build_context_message(user_id, user_message)
            
            # AI 응답 생성 (타임아웃 걱정 없음)
            response = model.generate_content(context_message)
            
            if not response or not response.text:
                return "죄송합니다. AI가 응답을 생성하지 못했습니다."
            
            ai_response = response.text
            
            # 대화 기록 저장
            GeminiAI.save_conversation(user_id, user_message, ai_response)
            
            return ai_response
            
        except Exception as e:
            logging.error(f"Gemini API 오류: {e}")
            return f"AI 서비스 오류가 발생했습니다: {str(e)}"

    @staticmethod
    def clear_conversation(user_id):
        """대화 기록 삭제"""
        if user_id in conversations:
            del conversations[user_id]
            return True
        return False

print("GeminiAI 클래스 로딩 완료")