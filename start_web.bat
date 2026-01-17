@echo off
REM 启动Web管理界面 (Windows)

cd /d "%~dp0"

echo ========================================
echo   用户生日和祝福数据管理系统
echo ========================================
echo.
echo 正在启动Web管理界面...
echo 访问地址: http://127.0.0.1:5000
echo 按 Ctrl+C 停止服务
echo.

python app.py

pause
