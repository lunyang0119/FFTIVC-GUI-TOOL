# FFT/FF16 번역 도구 올인원 GUI 프로그램

파이썬을 모르는 일반 사용자도 FFT/FF16 게임 파일의 번역 작업을 쉽게 수행할 수 있도록 하는 GUI 기반 올인원 도구입니다.
아직 베타버전으로, 오류가 있다면 Issues나 nie600s@naver.com으로 메일주시면 감사합니다.
readme는 아직 업데이트 중입니다.

## 주요 기능

- PAC 파일 언팩/팩
- NXD/PZD 파일을 JSON/YAML로 변환
- JSON/YAML을 CSV로 변환하여 번역 작업 수행
- CSV 검증 (일본어 문자 탐지)
- 번역 적용 및 재팩킹

## 설치 방법

### 1. Python 설치
Python 3.10 이상이 필요합니다.

### 2. ⚠️ .NET Runtime 설치 (중요!)
FF16Tools 실행을 위해 **.NET 9.0 Runtime**이 필요합니다.

**다운로드:** https://dotnet.microsoft.com/download/dotnet/9.0

### 4. 외부 도구 준비
다음 도구들을 다운로드하여 프로그램 폴더에 배치하세요:

- **FF16Tools**: https://github.com/Nenkai/FF16Tools
  - `ff16tools/` 폴더에 배치 (자동 탐지됨)
- **ffttic-nxdtext**: https://github.com/mmatyas/ffttic-nxdtext/releases
  - 프로그램 루트 폴더에 배치 (자동 탐지됨)
 
  최종적으로 파일 형태는 아래와 같아야합니다.

FFT_Translation_Tool/
├── ff16tools/  
│   ├── FF16Tools.CLI.exe
│   ├── # 내용물
├── fftic_nxdtext.exe
├── fftivc_allinone.exe

## 사용 방법

### 1. 프로그램 실행
releases에서 다운 받아 주세요.

### 2. 외부 도구 경로 설정
첫 실행 시 메뉴에서 설정 → FF16Tools 경로 설정 및 ffttic-nxdtext 경로를 설정하세요.

### 3. 작업 순서

#### 탭 1: PAC 변환
1. 원본 PAC 파일 또는 폴더 선택
2. 출력 폴더 선택
3. NXD/PZD 변환 옵션 선택
4. "언팩 및 변환 시작" 버튼 클릭

#### 탭 2: CSV 변환
1. YAML/JSON 파일이 있는 폴더 선택
2. CSV 저장 위치 선택
3. "CSV 생성" 버튼 클릭
4. 생성된 CSV 파일을 Excel 등으로 열어 번역 작업 수행

#### 탭 3: CSV 수정
1. csv의 translation 열에 일본어 문자가 있는지 검사
2. 필요시 일괄 문자 치환 수행

#### 탭 4: 번역 적용
1. 번역이 완료된 CSV 폴더 선택
2. 원본 YAML/JSON 폴더 선택
3. 최종 PAC 파일 저장 위치 선택
4. 처리 옵션 설정
5. "번역 적용 및 팩킹" 버튼 클릭

## CSV 파일 형식

생성되는 CSV 파일은 다음과 같은 형식을 가집니다:

```csv
Tag,FileName,EntryID,OriginalText,Translation
<text1>,movie0020.ja.yaml,357467,"太陽と聖印に護られた 双頭の獅子が治める国\n—イヴァリース",""
<text2>,achievement.ja.json,achievement/1/6,"<center>역사의 진실을 모두 탐구함으로써...</center>",""
```

- **Tag**: 자동 생성되는 텍스트 태그
- **FileName**: 원본 파일명
- **EntryID**: 엔트리 ID (PZD는 정수, NXD는 문자열)
- **OriginalText**: 원문
- **Translation**: 번역문 (여기에 번역 입력)

## 프로젝트 구조

```
fftivc_allinone_tool/
├── main.py                 # 메인 실행 파일
├── config.json            # 설정 파일
├── requirements.txt       # 의존성
├── README.md             # 이 문서
│
├── gui/                  # GUI 모듈
│   ├── main_window.py    # 메인 창
│   ├── tab_unpack.py     # 탭 1: PAC 변환
│   ├── tab_to_csv.py     # 탭 2: CSV 변환
│   ├── tab_csv_edit.py   # 탭 3: CSV 수정
│   └── tab_apply.py      # 탭 4: 번역 적용
│
├── core/                 # 핵심 로직
│   ├── config_manager.py # 설정 관리
│   ├── ff16tools_wrapper.py # FF16Tools 래퍼
│   ├── ffttic_wrapper.py # ffttic-nxdtext 래퍼
│   ├── pac_handler.py    # PAC 처리
│   ├── converter.py      # 파일 변환
│   ├── csv_handler.py    # CSV 처리
│   └── validator.py      # 검증
│
├── utils/                # 유틸리티
│   └── logger.py         # 로깅
│
└── logs/                 # 로그 파일

## 라이선스

MIT License

## 문의

이슈 발생 시 GitHub Issues에 등록해주세요.



