@echo off
cd C:\dlsite-auto
python auto_daily.py

REM GitHubに自動アップロード
git add index.html
git commit -m "Daily update %date% %time%"
git push origin main

pause