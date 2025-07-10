import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 환경변수에서 값 가져오기
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    PORT = int(os.getenv('PORT', 8000))
    
    # API 키 검증
    @classmethod
    def validate_keys(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다")
        if not cls.WEATHER_API_KEY:
            raise ValueError("WEATHER_API_KEY가 설정되지 않았습니다")
    
    # Gemini 설정
    GENERATION_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    }
    
    # 시스템 프롬프트
    SYSTEM_PROMPT = """숨. AI 어시스턴트입니다. 
    다음 규칙을 따라주세요:
    1. 친근하고 정중한 말투를 사용하세요
    2. 모르는 것은 솔직히 모른다고 하세요  
    3. 답변은 간결하면서도 유용하게 해주세요
    4. 한국어로 답변해주세요
    5. 카카오톡 메시지 특성상 너무 길지 않게 답변해주세요"""