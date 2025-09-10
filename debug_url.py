#!/usr/bin/env python3
"""
Отладка URL
"""

import requests

def debug_url():
    """Отлаживает URL"""
    print("🔍 Отладка URL")
    print("==============")
    
    url = "http://search.headcorn.pro/mockups/mockup_20250910_122129_modern.jpg"
    
    print(f"URL: {url}")
    
    # Тестируем разные User-Agent
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'curl/7.68.0',
        'Python-requests/2.31.0',
        None
    ]
    
    for i, ua in enumerate(user_agents, 1):
        print(f"\n{i}. User-Agent: {ua}")
        try:
            headers = {'User-Agent': ua} if ua else {}
            response = requests.head(url, timeout=5, headers=headers)
            print(f"   HTTP: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    # Тестируем GET вместо HEAD
    print(f"\n5. GET запрос:")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, timeout=5, headers=headers)
        print(f"   HTTP: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        print(f"   Размер ответа: {len(response.content)} байт")
    except Exception as e:
        print(f"   Ошибка: {e}")

if __name__ == "__main__":
    debug_url()
