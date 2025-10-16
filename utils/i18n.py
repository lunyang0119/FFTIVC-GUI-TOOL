"""
다국어 지원 모듈 (Internationalization)
"""
import json
from pathlib import Path
from utils.logger import get_logger


class I18n:
    """다국어 지원 클래스"""

    _instance = None
    _current_language = "ko"  # 기본 언어: 한국어
    _translations = {}

    def __new__(cls):
        """싱글톤 패턴"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """초기화"""
        if not hasattr(self, 'initialized'):
            self.logger = get_logger()
            self.lang_dir = Path(__file__).parent.parent / "languages"
            self.lang_dir.mkdir(exist_ok=True)

            # config.json에서 언어 설정 로드
            initial_lang = self._load_language_from_config()
            self.load_language(initial_lang)
            self.initialized = True

    def _load_language_from_config(self):
        """config.json에서 언어 설정 로드"""
        try:
            config_file = Path(__file__).parent.parent / "config.json"
            if config_file.exists():
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    lang = config.get('language', 'ko')
                    self.logger.info(f"config.json에서 언어 설정 로드: {lang}")
                    return lang
        except Exception as e:
            self.logger.warning(f"config.json 언어 설정 로드 실패: {e}")

        # 기본값 반환
        return self._current_language

    def load_language(self, lang_code):
        """
        언어 파일 로드

        Args:
            lang_code: 언어 코드 (ko, en 등)
        """
        lang_file = self.lang_dir / f"{lang_code}.json"

        if not lang_file.exists():
            self.logger.warning(f"언어 파일을 찾을 수 없음: {lang_file}")
            # 기본 언어로 폴백
            if lang_code != "ko":
                self.load_language("ko")
            return

        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                self._translations = json.load(f)
                self._current_language = lang_code
                self.logger.info(f"언어 로드됨: {lang_code}")
        except Exception as e:
            self.logger.error(f"언어 파일 로드 실패: {e}")
            self._translations = {}

    def set_language(self, lang_code):
        """
        언어 설정

        Args:
            lang_code: 언어 코드 (ko, en 등)
        """
        self.load_language(lang_code)

    def get_language(self):
        """현재 언어 코드 반환"""
        return self._current_language

    def t(self, key, **kwargs):
        """
        번역 텍스트 가져오기

        Args:
            key: 번역 키 (점 표기법 지원, 예: "menu.file.open")
            **kwargs: 포맷팅 인자

        Returns:
            번역된 텍스트
        """
        # 점 표기법으로 중첩된 딕셔너리 탐색
        keys = key.split(".")
        value = self._translations

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # 키를 찾을 수 없으면 키 자체를 반환
                self.logger.warning(f"번역 키를 찾을 수 없음: {key}")
                return key

        # 문자열이 아니면 키 반환
        if not isinstance(value, str):
            return key

        # 포맷팅 적용
        try:
            return value.format(**kwargs)
        except Exception as e:
            self.logger.error(f"번역 포맷팅 실패: {key}, {e}")
            return value

    def get_available_languages(self):
        """사용 가능한 언어 목록 반환"""
        langs = []
        for lang_file in self.lang_dir.glob("*.json"):
            lang_code = lang_file.stem
            langs.append(lang_code)
        return sorted(langs)


# 전역 인스턴스
_i18n = I18n()


def t(key, **kwargs):
    """
    번역 텍스트 가져오기 (단축 함수)

    Args:
        key: 번역 키
        **kwargs: 포맷팅 인자

    Returns:
        번역된 텍스트
    """
    return _i18n.t(key, **kwargs)


def set_language(lang_code):
    """언어 설정"""
    _i18n.set_language(lang_code)


def get_language():
    """현재 언어 코드 반환"""
    return _i18n.get_language()


def get_available_languages():
    """사용 가능한 언어 목록 반환"""
    return _i18n.get_available_languages()
