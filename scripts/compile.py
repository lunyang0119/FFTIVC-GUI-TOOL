import re

jp_pattern = re.compile(r"[\u3040-\u30FF\u4E00-\u9FFF]")

def contains_japanese(text: str) -> bool:
    """텍스트에 일본어(히라/카나/한자)가 포함되어 있으면 True."""
    return bool(jp_pattern.search(text))

def find_japanese(text: str) -> list:
    """텍스트에서 매칭된 일본어 문자 목록을 반환."""
    return jp_pattern.findall(text)

def remove_japanese(text: str, repl: str = "") -> str:
    """일본어 문자를 제거하거나 repl로 대체."""
    return jp_pattern.sub(repl, text)

if __name__ == "__main__":
    samples = ["Hello", "こんにちは", "漢字とかな", "Mix: testテスト"]
    for s in samples:
        print(s)
        print("  contains:", contains_japanese(s))
        print("  found:", find_japanese(s))
        print("  clean:", remove_japanese(s))
        print()