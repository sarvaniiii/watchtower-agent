import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from config import THRESHOLDS, WEATHER_API_KEY, OPENWEATHER_API_KEY
import random

class WatchtowerAgent:
    def __init__(self):
        self.agent_name = "WATCHTOWER"
        self.last_alert = None
        self.alert_count = 0
        
    def fetch_signal(self, location: str, use_mock: bool = True) -> Dict[str, Any]:
        """
        Fetch disaster data from APIs or use mock data for demo
        """
        if use_mock or not WEATHER_API_KEY:
            return self._fetch_mock_data(location)
        else:
            return self._fetch_real_weather_data(location)
    
    def _fetch_mock_data(self, location: str) -> Dict[str, Any]:
        """Generate realistic mock disaster data"""
        mock_disasters = [
            {
                "type": "hurricane",
                "wind_speed": random.randint(60, 180),
                "precipitation": random.randint(20, 100),
                "pressure": random.randint(950, 1010),
                "confidence": round(random.uniform(0.7, 0.95), 2)
            },
            {
                "type": "earthquake",
                "magnitude": round(random.uniform(3.0, 8.0), 1),
                "depth": random.randint(1, 100),
                "confidence": round(random.uniform(0.6, 0.9), 2)
            },
            {
                "type": "flood",
                "water_level": round(random.uniform(1.0, 5.0), 1),
                "precipitation": random.randint(40, 200),
                "confidence": round(random.uniform(0.8, 0.98), 2)
            }
        ]
        
        disaster = random.choice(mock_disasters)
        disaster["location"] = location
        disaster["timestamp"] = datetime.utcnow().isoformat()
        
        return disaster
    
    def _fetch_real_weather_data(self, location: str) -> Dict[str, Any]:
        """Fetch real weather data from WeatherAPI"""
        try:
            url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            return {
                "type": "weather",
                "location": location,
                "wind_speed": data["current"]["wind_kph"],
                "precipitation": data["current"]["precip_mm"],
                "temperature": data["current"]["temp_c"],
                "humidity": data["current"]["humidity"],
                "condition": data["current"]["condition"]["text"],
                "confidence": 0.85,
                "timestamp": datetime.utcnow().isoformat()
            }
        except:
            return self._fetch_mock_data(location)
    
    def analyze_signal(self, data: Dict[str, Any]) -> str:
        """
        Analyze data against thresholds and classify severity
        Returns: "SAFE", "WARNING", or "CRITICAL"
        """
        if data["type"] == "hurricane" or data["type"] == "weather":
            wind_speed = data.get("wind_speed", 0)
            
            if wind_speed > THRESHOLDS["wind_speed"] * 1.5:
                return "CRITICAL"
            elif wind_speed > THRESHOLDS["wind_speed"]:
                return "WARNING"
                
        elif data["type"] == "earthquake":
            magnitude = data.get("magnitude", 0)
            
            if magnitude > THRESHOLDS["earthquake"]:
                return "CRITICAL"
            elif magnitude > THRESHOLDS["earthquake"] * 0.8:
                return "WARNING"
                
        elif data["type"] == "flood":
            precipitation = data.get("precipitation", 0)
            
            if precipitation > THRESHOLDS["precipitation"] * 1.5:
                return "CRITICAL"
            elif precipitation > THRESHOLDS["precipitation"]:
                return "WARNING"
        
        return "SAFE"
    
    def generate_alert(self, severity: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create standardized alert payload
        """
        event_type = data["type"].upper()
        
        alert = {
            "agent": self.agent_name,
            "status": severity,
            "event_type": event_type,
            "location": data["location"],
            "severity": self._map_severity_level(severity, data),
            "confidence": data.get("confidence", 0.75),
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": self._extract_metrics(data),
            "alert_id": f"ALERT-{datetime.utcnow().strftime('%Y%m%d')}-{self.alert_count:03d}"
        }
        
        self.last_alert = alert
        self.alert_count += 1
        
        return alert
    
    def _map_severity_level(self, severity: str, data: Dict[str, Any]) -> str:
        """Map severity to levels for display"""
        if severity == "CRITICAL":
            return "HIGH"
        elif severity == "WARNING":
            return "MEDIUM"
        return "LOW"
    
    def _extract_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from data"""
        metrics = {}
        
        if data["type"] in ["hurricane", "weather"]:
            metrics["wind_speed_kmh"] = data.get("wind_speed", 0)
            metrics["precipitation_mm"] = data.get("precipitation", 0)
            
        elif data["type"] == "earthquake":
            metrics["magnitude"] = data.get("magnitude", 0)
            metrics["depth_km"] = data.get("depth", 0)
            
        elif data["type"] == "flood":
            metrics["precipitation_mm"] = data.get("precipitation", 0)
            metrics["water_level_m"] = data.get("water_level", 0)
            
        return metrics
    
    def emit_log(self, alert: Dict[str, Any], data: Dict[str, Any]) -> str:
        """
        Generate human-readable log message
        """
        status_emoji = "🚨" if alert["status"] == "CRITICAL" else "⚠️" if alert["status"] == "WARNING" else "✅"
        
        log_msg = f"""[{self.agent_name}] {status_emoji} {alert['status']} EVENT DETECTED
Location: {alert['location']}
Event Type: {data['type'].title()}
Severity: {alert['severity']}
Confidence: {alert['confidence']*100:.1f}%
Timestamp: {alert['timestamp']}
Alert ID: {alert['alert_id']}
"""
        
        # Add specific metrics
        if data["type"] in ["hurricane", "weather"]:
            log_msg += f"Wind Speed: {data.get('wind_speed', 0)} km/h\n"
        elif data["type"] == "earthquake":
            log_msg += f"Magnitude: {data.get('magnitude', 0)}\n"
        
        log_msg += f"\nForwarding alert to Auditor Agent..."
        
        return log_msg