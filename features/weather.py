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
            "서울": {"lat": 37.5665, "lon": 126.9780},
            "부산": {"lat": 35.1796, "lon": 129.0756},
            "대구": {"lat": 35.8714, "lon": 128.6014},
            "인천": {"lat": 37.4563, "lon": 126.7052},
            "광주": {"lat": 35.1595, "lon": 126.8526},
            "대전": {"lat": 36.3504, "lon": 127.3845},
            "울산": {"lat": 35.5384, "lon": 129.3114},
            "세종": {"lat": 36.4800, "lon": 127.2890},
            "경기": {"lat": 37.4138, "lon": 127.5183},
            "강원": {"lat": 37.8228, "lon": 128.1555},
            "충북": {"lat": 36.6357, "lon": 127.4917},
            "충남": {"lat": 36.5184, "lon": 126.8000},
            "전북": {"lat": 35.7175, "lon": 127.1530},
            "전남": {"lat": 34.8679, "lon": 126.9910},
            "경북": {"lat": 36.4919, "lon": 128.8889},
            "경남": {"lat": 35.4606, "lon": 128.2132},
            "제주": {"lat": 33.4996, "lon": 126.5312}
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