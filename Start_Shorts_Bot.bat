@echo off
title YouTube Shorts Bot Sunucusu
color 0A

echo ===================================================
echo     YOUTUBE SHORTS OTOMASYON BOTU BASLATILIYOR
echo ===================================================
echo.
echo Lutfen bu siyah pencereyi kapatmayin! 
echo Eger bu pencereyi kapatirsaniz bot durur ve site acilmaz.
echo.
echo Sunucu aciliyor, lutfen bekleyin...
echo.

:: Tarayıcıyı otomatik olarak aç
start "" "http://127.0.0.1:5000"

:: Flask sunucusunu başlat
.\venv\Scripts\python.exe src\app.py

pause
