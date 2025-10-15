# 빠른 시작 가이드

## EXE 파일 만들기 (개발자용)

### 한 줄로 빌드하기

```bash
build.bat
```

끝! `dist\FFT_Translation_Tool\` 폴더에 실행 파일이 생성됩니다.

---

## 배포 패키지 만들기

### 1. 빌드 실행
```bash
build.bat
```

### 2. 외부 도구 배치

```
dist\FFT_Translation_Tool\
├── ff16tools\               ← 이 폴더 생성 후
│   └── FF16Tools.CLI.exe   ← FF16Tools 배치
└── ffttic-nxdtext.exe      ← ffttic 배치
```

### 3. 압축
`dist\FFT_Translation_Tool\` 폴더 전체를 ZIP으로 압축

### 4. 배포
ZIP 파일을 사용자에게 전달

---

## 사용자 설치 방법 (최종 사용자용)

### 필수 설치

**1. .NET 9.0 Runtime 설치**
- https://dotnet.microsoft.com/download/dotnet/9.0
- "Download .NET Runtime 9.0" → x64 클릭
- 설치 후 PC 재시작

**2. 프로그램 압축 해제**
- 다운받은 ZIP 파일을 원하는 위치에 압축 해제
- 예: `C:\FFT_Tool\`

**3. 프로그램 실행**
- `FFT_Translation_Tool.exe` 더블클릭

---

## 사용 흐름

### 번역 작업 전체 과정

**1단계: 언팩 및 변환 (탭 1)**
```
PAC 파일 선택 → 출력 폴더 자동 설정 → "언팩 및 변환 시작"
→ NXD → JSON, PZD → YAML 변환됨
```

**2단계: CSV 생성 (탭 2)**
```
JSON/YAML 폴더 선택 → CSV 저장 위치 선택 → "CSV 생성"
→ 번역 작업용 CSV 파일 생성됨
```

**3단계: CSV 번역**
```
CSV 파일을 Excel이나 Google Sheets로 열기
→ Translation 열에 번역 입력
→ 저장
```

**4단계: CSV 검증 (탭 3, 선택사항)**
```
CSV 폴더 선택 → "일본어 문자 검사"
→ 누락된 번역 확인
```

**5단계: 번역 적용 및 팩킹 (탭 4)**
```
CSV 폴더 선택 → 원본 JSON/YAML 폴더 선택 → 출력 폴더 선택
→ "번역 적용 및 팩킹"
→ 번역된 PAC 파일 생성됨
```

---

## 문제 해결

### 프로그램이 실행되지 않음
- .NET 9.0 Runtime 설치 확인
- 백신 프로그램 예외 설정

### 언팩 실패
- .NET 9.0 Runtime 설치 확인
- FF16Tools 경로 확인: `설정` → `FF16Tools 경로 설정`

### NXD 변환 실패
- ffttic-nxdtext.exe가 프로그램 폴더에 있는지 확인

자세한 내용은 `TROUBLESHOOTING.md` 참조

---

## 폴더 구조 (최종)

```
FFT_Translation_Tool\
│
├── FFT_Translation_Tool.exe     ← 메인 실행 파일
│
├── ff16tools\                    ← FF16Tools (사용자가 배치)
│   ├── FF16Tools.CLI.exe
│   └── (기타 파일들)
│
├── ffttic-nxdtext.exe           ← NXD 변환 도구 (사용자가 배치)
│
├── config.json                   ← 자동 생성되는 설정 파일
├── logs\                         ← 자동 생성되는 로그 폴더
│
├── README.md
├── TROUBLESHOOTING.md
└── (PyInstaller가 생성한 DLL들)
```

---

## 주요 기능

### 탭 1: PAC 변환
- PAC 언팩
- NXD → JSON 변환
- PZD → YAML 변환
- **신규**: 독립 변환 기능 (언팩 없이 변환만 가능)

### 탭 2: CSV 변환
- JSON → CSV
- YAML → CSV
- 하위 폴더 포함 옵션

### 탭 3: CSV 수정
- 일본어 문자 검증
- 일괄 문자 치환
- 검증 결과 TXT 저장

### 탭 4: 번역 적용
- CSV → JSON/YAML 적용
- JSON → NXD 변환
- YAML → PZD 변환
- PAC 팩킹
- 중간 파일 자동 정리

---

## 팁

1. **처음 실행 시**: 설정 메뉴에서 외부 도구 경로를 확인하세요 (자동 탐지됨)
2. **언팩 폴더**: PAC 파일명으로 자동 생성됩니다
3. **프로그레스바**: 실시간 진행 상황을 표시합니다
4. **로그**: 상세한 작업 내역은 `logs\` 폴더에 저장됩니다

---

## 라이선스

MIT License

파이썬 모르는 사람도 쉽게 사용할 수 있도록 만든 도구입니다!
