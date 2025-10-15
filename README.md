# FFT/FF16 번역 도구 올인원 GUI 프로그램

파이썬을 모르는 일반 사용자도 FFT/FF16 게임 파일의 번역 작업을 쉽게 수행할 수 있도록 하는 GUI 기반 올인원 도구입니다.

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

**설치 확인:**
```bash
dotnet --list-runtimes
```
출력에 `Microsoft.NETCore.App 9.0.x`가 있어야 합니다.

### 3. Python 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 외부 도구 준비
다음 도구들을 다운로드하여 프로그램 폴더에 배치하세요:

- **FF16Tools**: https://github.com/Nenkai/FF16Tools
  - `ff16tools/` 폴더에 배치 (자동 탐지됨)
- **ffttic-nxdtext**: https://github.com/mmatyas/ffttic-nxdtext/releases
  - 프로그램 루트 폴더에 배치 (자동 탐지됨)

## 사용 방법

### 1. 프로그램 실행
```bash
python main.py
```

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
1. CSV 파일 검증 (일본어 문자 검사)
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

## 중요 사항

1. **NXD 파일 변환**: 절대 FF16Tools로 NXD를 변환하지 마세요! ffttic-nxdtext만 사용하세요.
2. **원본 NXD 보존**: JSON → NXD 변환 시 원본 NXD 파일이 필요하므로 보존하세요.
3. **백업**: 작업 전 항상 원본 파일을 백업하세요.
4. **문자 인코딩**: CSV 파일은 UTF-8 with BOM으로 저장됩니다 (Excel 호환).

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
```

## 개발 현황

### Phase 1: 기본 구조 ✅ 완료
- [x] 프로젝트 디렉토리 구조 생성
- [x] PyQt6 메인 윈도우 구현
- [x] 4개 탭 레이아웃 구현
- [x] 설정 관리 시스템 구현
- [x] 기본 로깅 시스템 구현

### Phase 2: 핵심 기능 ✅ 완료
- [x] FF16Tools 래퍼 클래스 구현
- [x] ffttic-nxdtext 래퍼 클래스 구현
- [x] PAC 언팩/팩 기능 구현
- [x] JSON/YAML ↔ CSV 변환 기능 구현
- [x] CSV 검증 및 일괄 치환 기능
- [x] 번역 적용 및 재팩킹 기능

### Phase 3: TODO
- [ ] 탭별 실제 로직 연결
- [ ] 프로그레스 바 및 실시간 로그 출력
- [ ] 에러 처리 개선
- [ ] UI/UX 개선

## 라이선스

MIT License

## 문의

이슈 발생 시 GitHub Issues에 등록해주세요.

## 참고

- FF16Tools: https://github.com/Nenkai/FF16Tools
- ffttic-nxdtext: 별도 제공

