@echo off
@chcp 65001 1> NUL 2> NUL
echo ====================================
echo FFT Translation Tool - Build Script
echo ====================================
echo.

REM 1. PyInstaller 설치 확인
echo [1/4] PyInstaller 설치 확인...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller가 설치되어 있지 않습니다. 설치를 시작합니다...
    pip install pyinstaller
) else (
    echo PyInstaller가 이미 설치되어 있습니다.
)
echo.

REM 2. 기존 빌드 결과 삭제
echo [2/4] 기존 빌드 결과 삭제...
if exist "dist" (
    rmdir /s /q dist
    echo dist 폴더 삭제 완료
)
if exist "build" (
    rmdir /s /q build
    echo build 폴더 삭제 완료
)
echo.

REM 3. PyInstaller로 빌드
echo [3/4] PyInstaller로 빌드 중...
pyinstaller fftivc_tool.spec
if errorlevel 1 (
    echo 빌드 실패!
    pause
    exit /b 1
)
echo.

REM 4. 필요한 파일 복사
echo [4/4] 필요한 파일 복사...

REM config.json이 없으면 생성
if not exist "dist\FFT_Translation_Tool\config.json" (
    copy config.json "dist\FFT_Translation_Tool\" >nul
    echo config.json 복사 완료
)

REM logs 폴더 생성
if not exist "dist\FFT_Translation_Tool\logs" (
    mkdir "dist\FFT_Translation_Tool\logs"
    echo logs 폴더 생성 완료
)

REM README 복사
if exist "README.md" (
    copy README.md "dist\FFT_Translation_Tool\" >nul
    echo README.md 복사 완료
)

REM TROUBLESHOOTING 복사
if exist "TROUBLESHOOTING.md" (
    copy TROUBLESHOOTING.md "dist\FFT_Translation_Tool\" >nul
    echo TROUBLESHOOTING.md 복사 완료
)

REM languages 폴더 확인 및 복사 (백업용)
REM .spec 파일에 이미 포함되어 있지만, 혹시 모를 경우를 대비해 수동 복사
if exist "languages\en.json" (
    if not exist "dist\FFT_Translation_Tool\_internal\languages" (
        mkdir "dist\FFT_Translation_Tool\_internal\languages"
    )
    copy "languages\en.json" "dist\FFT_Translation_Tool\_internal\languages\" > nul 2>&1
    copy "languages\ko.json" "dist\FFT_Translation_Tool\_internal\languages\" > nul 2>&1
    if exist "dist\FFT_Translation_Tool\_internal\languages\en.json" (
        echo languages 폴더 확인 완료
    ) else (
        echo WARNING: languages 파일 복사 실패!
    )
)

echo.
echo ====================================
echo 빌드 완료!
echo ====================================
echo.
echo 실행 파일 위치: dist\FFT_Translation_Tool\FFT_Translation_Tool.exe
echo.
echo 배포 방법:
echo 1. dist\FFT_Translation_Tool 폴더 전체를 압축
echo 2. 폴더 내에 ff16tools 폴더를 생성하고 FF16Tools.CLI.exe 배치
echo 3. 폴더 내에 ffttic-nxdtext.exe 배치
echo 4. 사용자에게 전달
echo.
pause
