# FFTIVC 번역 도구 올인원 GUI 프로그램

파이썬을 모르는 일반 사용자도 FFTIVC(Advaced Only) 파일의 번역 작업을 쉽게 수행할 수 있도록 하는 GUI 기반 올인원 도구입니다.
아직 베타버전으로(아마 영원히), 의문점이나 오류가 있다면 Issues나 https://open.kakao.com/me/lusisseaweed
으로 연락주시면 감사하겠습니다.
(오픈채팅이 더 확인이 빠릅니다.)
readme는 아직 업데이트 중입니다.

0004.ja.pac을 모딩하는 것을 전제로 만들어졌기에 다른 PAC 파일과 호환되지 않을 수 있습니다. (특히 CSV 추출)

또한 이 툴은 불완전하기 때문에 꼭 **원본 파일을 백업한 후 사용해주세요!**

**오류가 많습니다! 감안하고 사용해주세요! 오류제보는 위에 적혀진 곳으로 받고 있습니다.**

**There is also an English version. (Incomplete)**




## 주요 기능

- PAC 파일 언팩/팩
- NXD/PZD 파일을 JSON/YAML로 변환
- JSON/YAML을 CSV로 변환하여 번역 작업 수행
- CSV 검증 (일본어 문자 탐지)
- 번역 적용 및 재팩킹

## 설치 방법

### 1. ⚠️ .NET Runtime 설치 (중요!)
FF16Tools 실행을 위해 **.NET 9.0 Runtime**이 필요합니다.

**다운로드:** https://dotnet.microsoft.com/download/dotnet/9.0

### 2. 외부 도구 준비
다음 도구들을 다운로드하여 프로그램 폴더에 배치하세요:

- **FF16Tools**: https://github.com/Nenkai/FF16Tools
  - `ff16tools/` 폴더
- **ffttic-nxdtext**: https://github.com/mmatyas/ffttic-nxdtext/releases/tag/v1.0

**반드시 1.0 버전을 다운로드 받으셔야 합니다!** 현재 호환성 이슈로 최신버전은 사용할 수 없습니다. (추후에 고칠 예정)
  - 프로그램 루트 폴더에 배치
  
  최종 파일 형태는 아래와 같아야합니다.

FFT_Translation_Tool/

├── ff16tools/  **폴더 이름을 ff16tools로 바꿔주셔야합니다**

│   ├── FF16Tools.CLI.exe

│   ├── # 내용물

├── fftic_nxdtext.exe

├── fftivc_allinone.exe

## 사용 방법

### 1. 프로그램 실행
releases에서 다운 받아 주세요.

### 2. 외부 도구 경로 설정
위의 기재된 대로 파일이 정리되어있지 않다면, 설정에서 따로 설정해주시면 됩니다.

### 3. 작업 순서

#### 탭 1: PAC 변환
1. 원본 PAC 파일 또는 폴더 선택
2. 언패킹한 파일 놔둘 폴더 선택
3. NXD/PZD 변환 옵션 선택
4. "언팩 및 변환 시작" 버튼 클릭


#### 탭 2: CSV 변환
1. YAML/JSON 파일이 있는 폴더 선택
2. CSV 저장 위치 선택
3. "CSV 생성" 버튼 클릭
4. 생성된 CSV 파일을 Excel 등으로 열어 번역 작업 수행 (저장하는 과정에서 인코딩에 문제가 생길 수 있으니 확인해주세요!)

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

- **Tag**: 자동 생성되는 텍스트 태그. 태그에 따라 어떤 파일에 적용될지 달라집니다.
- **FileName**: 원본 파일명
- **EntryID**: 엔트리 ID (PZD는 정수, NXD는 문자열)
- **OriginalText**: 원문
- **Translation**: 번역문.

## 라이선스

MIT License


