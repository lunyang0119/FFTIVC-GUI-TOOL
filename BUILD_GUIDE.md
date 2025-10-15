# EXE 빌드 및 배포 가이드

## 개발자용: EXE 파일 빌드 방법

### 1. 사전 준비

**필수 설치:**
- Python 3.10 이상
- 모든 의존성 패키지

```bash
pip install -r requirements.txt
```

### 2. 빌드 실행

**Windows:**
```bash
build.bat
```

빌드가 완료되면 `dist\FFT_Translation_Tool\` 폴더에 실행 파일이 생성됩니다.

### 3. 빌드 결과 확인

```
dist\FFT_Translation_Tool\
├── FFT_Translation_Tool.exe  ← 실행 파일
├── config.json
├── logs\
├── README.md
├── TROUBLESHOOTING.md
└── (기타 PyInstaller가 생성한 파일들)
```

### 4. 배포 패키지 준비

1. **외부 도구 배치:**
   ```
   dist\FFT_Translation_Tool\
   ├── ff16tools\
   │   ├── FF16Tools.CLI.exe
   │   └── (기타 FF16Tools 파일들)
   ├── ffttic-nxdtext.exe
   └── FFT_Translation_Tool.exe
   ```

2. **배포 가이드 작성:**
   - `DISTRIBUTION_README.txt` 생성 (아래 참조)

3. **압축:**
   ```bash
   # 전체 폴더를 ZIP으로 압축
   FFT_Translation_Tool_v1.0.zip
   ```

## 사용자용: 배포 패키지 구조

### 다운로드 후 폴더 구조

```
FFT_Translation_Tool\
├── FFT_Translation_Tool.exe      ← 이 파일을 실행하세요!
├── ff16tools\
│   └── FF16Tools.CLI.exe
├── ffttic-nxdtext.exe
├── config.json
├── logs\
├── README.md
├── TROUBLESHOOTING.md
└── (기타 필요한 DLL 파일들)
```

### 설치 및 실행 방법

**1. 사전 준비 (.NET Runtime 설치)**

⚠️ **중요: .NET 9.0 Runtime이 필요합니다!**

다운로드: https://dotnet.microsoft.com/download/dotnet/9.0

**설치 확인:**
```bash
dotnet --list-runtimes
```

출력에 `Microsoft.NETCore.App 9.0.x`가 있어야 합니다.

**2. 외부 도구 다운로드 (이미 포함되어 있지 않은 경우)**

- **FF16Tools**: https://github.com/Nenkai/FF16Tools
  - Releases에서 최신 버전 다운로드
  - `ff16tools\` 폴더에 압축 해제

- **ffttic-nxdtext**: (별도 제공)
  - 프로그램 폴더 루트에 배치

**3. 프로그램 실행**

`FFT_Translation_Tool.exe`를 더블클릭하여 실행

## 배포 체크리스트

배포 전 다음 사항을 확인하세요:

- [ ] .NET 9.0 Runtime 요구사항을 README에 명시
- [ ] FF16Tools.CLI.exe가 `ff16tools\` 폴더에 포함됨
- [ ] ffttic-nxdtext.exe가 루트 폴더에 포함됨
- [ ] config.json이 포함됨
- [ ] README.md와 TROUBLESHOOTING.md가 포함됨
- [ ] 깨끗한 환경에서 테스트 완료

## 배포용 README 템플릿

다음 내용으로 `DISTRIBUTION_README.txt`를 생성하세요:

```
====================================
FFT/FF16 번역 도구 v1.0
====================================

파이썬 설치 없이 사용 가능한 FFT/FF16 게임 파일 번역 도구입니다.

【설치 방법】

1. .NET 9.0 Runtime 설치 (필수!)
   다운로드: https://dotnet.microsoft.com/download/dotnet/9.0

   설치 확인:
   - 명령 프롬프트에서 "dotnet --list-runtimes" 입력
   - "Microsoft.NETCore.App 9.0.x" 확인

2. 프로그램 실행
   - FFT_Translation_Tool.exe 더블클릭

【폴더 구조】

FFT_Translation_Tool\
├── FFT_Translation_Tool.exe      ← 실행 파일
├── ff16tools\                      ← FF16Tools
│   └── FF16Tools.CLI.exe
├── ffttic-nxdtext.exe             ← NXD 변환 도구
└── (기타 파일들)

【문제 해결】

문제가 발생하면 TROUBLESHOOTING.md를 참고하세요.

【라이선스】

MIT License

【문의】

GitHub Issues: (저장소 URL)
```

## 문제 해결

### 빌드 실패

**증상:** PyInstaller 실행 중 오류 발생

**해결:**
1. 가상환경 사용 권장
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. 캐시 삭제 후 재시도
   ```bash
   rmdir /s /q build dist
   build.bat
   ```

### 실행 파일이 실행되지 않음

**증상:** EXE 파일 더블클릭 시 아무 반응 없음

**해결:**
1. 콘솔 모드로 빌드하여 오류 확인
   - `fftivc_tool.spec` 파일에서 `console=True`로 변경
   - 재빌드

2. 백신 프로그램 확인
   - 일부 백신이 PyInstaller 실행 파일을 차단할 수 있음

### DLL 누락 오류

**증상:** "DLL을 찾을 수 없습니다" 오류

**해결:**
- Visual C++ Redistributable 설치
- https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist

## 고급 설정

### 아이콘 변경

1. ICO 파일 준비 (예: `icon.ico`)
2. `fftivc_tool.spec` 수정:
   ```python
   icon='icon.ico',
   ```
3. 재빌드

### 단일 파일로 빌드

더 작은 배포 패키지를 원한다면:

`fftivc_tool.spec` 수정:
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,    # 추가
    a.zipfiles,    # 추가
    a.datas,       # 추가
    [],
    exclude_binaries=False,  # False로 변경
    name='FFT_Translation_Tool',
    ...
)

# COLLECT 블록 제거
```

**주의:** 단일 파일 빌드는 실행 시 압축 해제 시간이 필요하여 시작이 느릴 수 있습니다.

## 버전 관리

배포 시 버전 번호를 명확히 표시하세요:

1. `main.py`에 버전 상수 추가:
   ```python
   VERSION = "1.0.0"
   ```

2. 윈도우 타이틀에 버전 표시:
   ```python
   self.setWindowTitle(f"FFT/FF16 번역 도구 v{VERSION}")
   ```

3. 빌드 파일명에 버전 포함:
   ```
   FFT_Translation_Tool_v1.0.0.zip
   ```
