import requests
import json
from datetime import datetime, timedelta
from config import Config

class WeatherManager:
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError("OpenWeatherMap API 키가 설정되지 않았습니다")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        
        # 주요 도시 좌표 (한국)
        self.cities = {
        # 특별시/광역시/특별자치시
        "서울": {"lat": 37.5665, "lon": 126.9780},
        "부산": {"lat": 35.1796, "lon": 129.0756},
        "대구": {"lat": 35.8714, "lon": 128.6014},
        "인천": {"lat": 37.4563, "lon": 126.7052},
        "광주": {"lat": 35.1595, "lon": 126.8526},
        "대전": {"lat": 36.3504, "lon": 127.3845},
        "울산": {"lat": 35.5384, "lon": 129.3114},
        "세종": {"lat": 36.4800, "lon": 127.2890},
        
        # 경기도 주요 도시
        "수원": {"lat": 37.2636, "lon": 127.0286},
        "성남": {"lat": 37.4449, "lon": 127.1388},
        "용인": {"lat": 37.2341, "lon": 127.2769},
        "안양": {"lat": 37.3943, "lon": 126.9568},
        "안산": {"lat": 37.3236, "lon": 126.8219},
        "부천": {"lat": 37.5035, "lon": 126.7660},
        "고양": {"lat": 37.6584, "lon": 126.8320},
        "남양주": {"lat": 37.6369, "lon": 127.2158},
        "화성": {"lat": 37.1997, "lon": 126.8312},
        "평택": {"lat": 36.9923, "lon": 127.1128},
        "의정부": {"lat": 37.7380, "lon": 127.0332},
        "시흥": {"lat": 37.3800, "lon": 126.8031},
        "파주": {"lat": 37.7599, "lon": 126.7800},
        "김포": {"lat": 37.6157, "lon": 126.7159},
        "광명": {"lat": 37.4781, "lon": 126.8644},
        "군포": {"lat": 37.3617, "lon": 126.9356},
        "하남": {"lat": 37.5394, "lon": 127.2145},
        "오산": {"lat": 37.1499, "lon": 127.0776},
        "이천": {"lat": 37.2720, "lon": 127.4351},
        "안성": {"lat": 37.0078, "lon": 127.2797},
        "의왕": {"lat": 37.3449, "lon": 126.9689},
        "양주": {"lat": 37.7854, "lon": 127.0456},
        "구리": {"lat": 37.5943, "lon": 127.1296},
        "포천": {"lat": 37.8948, "lon": 127.2004},
        "동두천": {"lat": 37.9033, "lon": 127.0608},
        "과천": {"lat": 37.4292, "lon": 126.9876},
        "가평": {"lat": 37.8316, "lon": 127.5109},
        "양평": {"lat": 37.4914, "lon": 127.4874},
        "여주": {"lat": 37.2982, "lon": 127.6376},
        "연천": {"lat": 38.0965, "lon": 127.0741},
        
        # 강원도
        "춘천": {"lat": 37.8813, "lon": 127.7298},
        "원주": {"lat": 37.3422, "lon": 127.9202},
        "강릉": {"lat": 37.7519, "lon": 128.8761},
        "동해": {"lat": 37.5247, "lon": 129.1144},
        "태백": {"lat": 37.1640, "lon": 128.9856},
        "속초": {"lat": 38.2070, "lon": 128.5918},
        "삼척": {"lat": 37.4499, "lon": 129.1658},
        
        # 충청북도
        "청주": {"lat": 36.6424, "lon": 127.4890},
        "충주": {"lat": 36.9910, "lon": 127.9259},
        "제천": {"lat": 37.1327, "lon": 128.1910},
        
        # 충청남도
        "천안": {"lat": 36.8151, "lon": 127.1139},
        "공주": {"lat": 36.4465, "lon": 127.1189},
        "보령": {"lat": 36.3333, "lon": 126.6127},
        "아산": {"lat": 36.7898, "lon": 127.0020},
        "서산": {"lat": 36.7848, "lon": 126.4503},
        "논산": {"lat": 36.1874, "lon": 127.0987},
        "계룡": {"lat": 36.2744, "lon": 127.2487},
        "당진": {"lat": 36.8934, "lon": 126.6278},
        
        # 전라북도
        "전주": {"lat": 35.8242, "lon": 127.1480},
        "군산": {"lat": 35.9677, "lon": 126.7369},
        "익산": {"lat": 35.9483, "lon": 126.9576},
        "정읍": {"lat": 35.5697, "lon": 126.8557},
        "남원": {"lat": 35.4163, "lon": 127.3906},
        "김제": {"lat": 35.8038, "lon": 126.8807},
        
        # 전라남도
        "목포": {"lat": 34.8118, "lon": 126.3922},
        "여수": {"lat": 34.7604, "lon": 127.6622},
        "순천": {"lat": 34.9507, "lon": 127.4872},
        "나주": {"lat": 35.0160, "lon": 126.7108},
        "광양": {"lat": 34.9407, "lon": 127.5956},
        
        # 경상북도
        "포항": {"lat": 36.0190, "lon": 129.3435},
        "경주": {"lat": 35.8562, "lon": 129.2247},
        "김천": {"lat": 36.1396, "lon": 128.1136},
        "안동": {"lat": 36.5684, "lon": 128.7294},
        "구미": {"lat": 36.1197, "lon": 128.3441},
        "영주": {"lat": 36.8056, "lon": 128.6239},
        "영천": {"lat": 35.9733, "lon": 128.9386},
        "상주": {"lat": 36.4107, "lon": 128.1590},
        "문경": {"lat": 36.5867, "lon": 128.1867},
        "경산": {"lat": 35.8252, "lon": 128.7417},
        
        # 경상남도 (김해 포함!)
        "창원": {"lat": 35.2284, "lon": 128.6811},
        "진주": {"lat": 35.1800, "lon": 128.1076},
        "통영": {"lat": 34.8544, "lon": 128.4331},
        "사천": {"lat": 35.0036, "lon": 128.0642},
        "김해": {"lat": 35.2342, "lon": 128.8898},
        "밀양": {"lat": 35.5038, "lon": 128.7465},
        "거제": {"lat": 34.8806, "lon": 128.6212},
        "양산": {"lat": 35.3350, "lon": 129.0375},
        
        # 제주특별자치도
        "제주": {"lat": 33.4996, "lon": 126.5312},
        "서귀포": {"lat": 33.2541, "lon": 126.5060},
        
        # 해외 주요 도시 (보너스)
        "도쿄": {"lat": 35.6762, "lon": 139.6503},
        "오사카": {"lat": 34.6937, "lon": 135.5023},
        "베이징": {"lat": 39.9042, "lon": 116.4074},
        "상하이": {"lat": 31.2304, "lon": 121.4737},
        "홍콩": {"lat": 22.3193, "lon": 114.1694},
        "싱가포르": {"lat": 1.3521, "lon": 103.8198},
        "뉴욕": {"lat": 40.7128, "lon": -74.0060},
        "런던": {"lat": 51.5074, "lon": -0.1278},
        "파리": {"lat": 48.8566, "lon": 2.3522},
        "로마": {"lat": 41.9028, "lon": 12.4964},
        "베를린": {"lat": 52.5200, "lon": 13.4050},
        "마드리드": {"lat": 40.4168, "lon": -3.7038},
        "암스테르담": {"lat": 52.3676, "lon": 4.9041},
        "시드니": {"lat": -33.8688, "lon": 151.2093},
        "멜번": {"lat": -37.8136, "lon": 144.9631},
        "밴쿠버": {"lat": 49.2827, "lon": -123.1207},
        "토론토": {"lat": 43.6532, "lon": -79.3832},
        "두바이": {"lat": 25.2048, "lon": 55.2708}
        }
        
        # 날씨 이모지 매핑
        self.weather_emojis = {
            "Clear": "☀️",
            "Clouds": "☁️", 
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Fog": "🌫️",
            "Haze": "🌫️"
        }
        
        # 날씨 설명 한글화
        self.weather_descriptions = {
            "clear sky": "맑음",
            "few clouds": "구름 조금",
            "scattered clouds": "구름 많음", 
            "broken clouds": "흐림",
            "overcast clouds": "매우 흐림",
            "light rain": "약한 비",
            "moderate rain": "보통 비",
            "heavy intensity rain": "강한 비",
            "very heavy rain": "매우 강한 비",
            "light snow": "약한 눈",
            "snow": "눈",
            "heavy snow": "폭설",
            "mist": "안개",
            "fog": "짙은 안개"
        }
    
    def get_current_weather(self, city="서울"):
        """현재 날씨 조회"""
        try:
            if city not in self.cities:
                available_cities = ", ".join(list(self.cities.keys())[:10])
                return f"❌ 지원하지 않는 도시입니다.\n\n🌍 지원 도시: {available_cities}..."
            
            lat = self.cities[city]["lat"]
            lon = self.cities[city]["lon"]
            
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "lang": "kr"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 데이터 파싱
            main = data["main"]
            weather = data["weather"][0]
            wind = data["wind"]
            
            temp = round(main["temp"])
            feels_like = round(main["feels_like"])
            humidity = main["humidity"]
            pressure = main["pressure"]
            wind_speed = round(wind.get("speed", 0) * 3.6, 1)  # m/s to km/h
            
            weather_main = weather["main"]
            weather_desc = weather["description"]
            
            # 이모지 선택
            emoji = self.weather_emojis.get(weather_main, "🌤️")
            
            # 한글 설명
            korean_desc = self.weather_descriptions.get(weather_desc, weather_desc)
            
            # 날씨 상태에 따른 조언
            advice = self.get_weather_advice(weather_main, temp, humidity)
            
            result = f"🌤️ **{city} 현재 날씨**\n\n"
            result += f"{emoji} {korean_desc}\n"
            result += f"🌡️ 온도: {temp}°C (체감 {feels_like}°C)\n"
            result += f"💧 습도: {humidity}%\n"
            result += f"🌪️ 바람: {wind_speed}km/h\n"
            result += f"📊 기압: {pressure}hPa\n\n"
            result += f"💡 **오늘의 팁**\n{advice}"
            
            return result
            
        except requests.exceptions.RequestException as e:
            return f"❌ 날씨 정보를 가져올 수 없습니다.\n네트워크 연결을 확인해주세요."
        except KeyError as e:
            return f"❌ 날씨 데이터 처리 중 오류가 발생했습니다."
        except Exception as e:
            return f"❌ 날씨 조회 오류: {str(e)}"
    
    def get_forecast(self, city="서울", days=3):
        """일기예보 (3일)"""
        try:
            if city not in self.cities:
                return f"❌ 지원하지 않는 도시입니다."
            
            lat = self.cities[city]["lat"]
            lon = self.cities[city]["lon"]
            
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "lang": "kr"
            }
            
            response = requests.get(self.forecast_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if "list" not in data or not data["list"]:
                return f"❌ {city}의 일기예보 데이터가 없습니다."
            
            if "cod" in data and data["cod"] != "200":
                return f"❌ API 오류: {data.get('message', '알 수 없는 오류')}"
            
            # 일별 예보 정리 (12시 기준)
            forecasts = []
            current_date = None
            
            for item in data["list"]:
                dt = datetime.fromtimestamp(item["dt"])
                date_str = dt.strftime("%Y-%m-%d")
                hour = dt.hour
                
                # 12시 데이터만 사용 (대표 시간)
                if hour == 12 and date_str != current_date:
                    current_date = date_str
                    
                    weather = item["weather"][0]
                    main = item["main"]
                    
                    forecasts.append({
                        "date": dt,
                        "temp_max": round(main["temp_max"]),
                        "temp_min": round(main["temp_min"]),
                        "weather": weather["main"],
                        "description": weather["description"],
                        "humidity": main["humidity"]
                    })
                    
                    if len(forecasts) >= days:
                        break
            
            if not forecasts:
                return f"❌ {city}의 일기예보를 가져올 수 없습니다."
            
            result = f"📅 **{city} {days}일 일기예보**\n\n"
            
            for forecast in forecasts:
                date = forecast["date"]
                day_name = ["월", "화", "수", "목", "금", "토", "일"][date.weekday()]
                date_str = date.strftime(f"%m/%d({day_name})")
                
                emoji = self.weather_emojis.get(forecast["weather"], "🌤️")
                korean_desc = self.weather_descriptions.get(forecast["description"], forecast["description"])
                
                result += f"{emoji} **{date_str}**\n"
                result += f"   {korean_desc}\n"
                result += f"   🌡️ {forecast['temp_min']}°C ~ {forecast['temp_max']}°C\n"
                result += f"   💧 습도 {forecast['humidity']}%\n\n"
            
            return result.strip()
            
        except Exception as e:
            return f"❌ 일기예보 조회 오류: {str(e)}"
    
    def get_weather_advice(self, weather_main, temp, humidity):
        """날씨별 조언"""
        advice = []
        
        # 온도별 조언
        if temp >= 30:
            advice.append("🔥 매우 더워요! 충분한 수분 섭취와 시원한 곳에서 쉬세요.")
        elif temp >= 25:
            advice.append("☀️ 더운 날씨예요. 가벼운 옷차림을 추천해요.")
        elif temp <= 0:
            advice.append("🧊 매우 추워요! 따뜻하게 입고 외출하세요.")
        elif temp <= 10:
            advice.append("🧥 쌀쌀해요. 외투를 챙기세요.")
        
        # 날씨별 조언
        if weather_main == "Rain":
            advice.append("☂️ 비가 와요! 우산을 꼭 챙기세요.")
        elif weather_main == "Snow":
            advice.append("⛄ 눈이 와요! 미끄러지지 않게 조심하세요.")
        elif weather_main == "Thunderstorm":
            advice.append("⚡ 천둥번개가 쳐요! 실내에 머무르세요.")
        
        # 습도별 조언
        if humidity >= 80:
            advice.append("💧 습도가 높아요. 통풍이 잘 되는 옷을 입으세요.")
        elif humidity <= 30:
            advice.append("🏜️ 건조해요. 수분 섭취와 보습에 신경 쓰세요.")
        
        return " ".join(advice) if advice else "좋은 하루 보내세요! 😊"
    
    def get_air_quality(self, city="서울"):
        """대기질 정보 (간단 버전)"""
        try:
            lat = self.cities[city]["lat"]
            lon = self.cities[city]["lon"]
            
            url = f"http://api.openweathermap.org/data/2.5/air_pollution"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            aqi = data["list"][0]["main"]["aqi"]
            
            # 대기질 지수 해석
            aqi_levels = {
                1: {"level": "좋음", "emoji": "😊", "color": "🟢"},
                2: {"level": "보통", "emoji": "😐", "color": "🟡"},
                3: {"level": "나쁨", "emoji": "😷", "color": "🟠"},
                4: {"level": "매우 나쁨", "emoji": "😨", "color": "🔴"},
                5: {"level": "위험", "emoji": "☠️", "color": "🟣"}
            }
            
            info = aqi_levels.get(aqi, {"level": "알 수 없음", "emoji": "❓", "color": "⚪"})
            
            return f"🌬️ **{city} 대기질**\n\n{info['color']} {info['level']} {info['emoji']}\n\n💡 외출 시 참고하세요!"
            
        except Exception as e:
            return f"❌ 대기질 정보 조회 오류: {str(e)}"
    
    def show_weather_menu(self):
        """날씨 메뉴"""
        cities_list = ", ".join(list(self.cities.keys())[:8])
        
        return f"""🌤️ **날씨 정보 센터**

☀️ **현재 날씨**
• `/날씨 현재 [도시]` - 현재 날씨
• `/날씨 [도시]` - 현재 날씨 (단축)

📅 **일기예보**
• `/날씨 예보 [도시]` - 3일 예보
• `/날씨 예보 [도시] [일수]` - 지정일 예보

🌬️ **대기질**
• `/날씨 대기질 [도시]` - 대기질 정보

🌍 **지원 도시**
{cities_list} 등

**사용 예시:**
• `/날씨 서울`
• `/날씨 현재 부산`
• `/날씨 예보 대구 5`
• `/날씨 대기질 인천`

어떤 지역의 날씨가 궁금하신가요? 🌈"""

    def parse_weather_command(self, command_parts):
        """날씨 명령어 파싱"""
        if len(command_parts) < 2:
            return self.show_weather_menu()
        
        cmd = command_parts[1].lower()
        
        try:
            # /날씨 [도시] (단축 명령)
            if cmd in self.cities:
                return self.get_current_weather(cmd)
            
            # /날씨 현재 [도시]
            elif cmd == "현재":
                city = command_parts[2] if len(command_parts) > 2 else "서울"
                return self.get_current_weather(city)
            
            # /날씨 예보 [도시] [일수]
            elif cmd == "예보":
                city = command_parts[2] if len(command_parts) > 2 else "서울"
                days = int(command_parts[3]) if len(command_parts) > 3 else 3
                days = min(max(days, 1), 5)  # 1-5일 제한
                return self.get_forecast(city, days)
            
            # /날씨 대기질 [도시]
            elif cmd == "대기질":
                city = command_parts[2] if len(command_parts) > 2 else "서울"
                return self.get_air_quality(city)
            
            else:
                return self.show_weather_menu()
                
        except (ValueError, IndexError):
            return "❌ 명령어 형식이 올바르지 않습니다.\n'/날씨'로 사용법을 확인해주세요."
        except Exception as e:
            return f"❌ 날씨 조회 중 오류: {str(e)}"