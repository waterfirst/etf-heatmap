@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ETF 모멘텀 히트맵 로컬 서버를 시작합니다...
python etf_server.py
if errorlevel 1 (
  echo.
  echo [안내] python 명령을 찾지 못했습니다. py 로 다시 시도합니다...
  py etf_server.py
)
pause
