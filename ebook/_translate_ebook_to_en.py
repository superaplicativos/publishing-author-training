from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import re

SRC = r"c:\Users\xberi\Desktop\VIDA-NOVA-RENDAEMDOLAR\rendaemdolar-main\ebook\ebook-renda-dolar-completo.html"
DST = r"c:\Users\xberi\Desktop\VIDA-NOVA-RENDAEMDOLAR\rendaemdolar-main\ebook\ebook-renda-dolar-completo-en.html"

with open(SRC, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
translator = GoogleTranslator(source="pt", target="en")

if soup.html:
    soup.html["lang"] = "en-US"

cache = {}


def should_translate_text(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    if re.fullmatch(r"[\d\W_]+", t):
        return False
    if "http://" in t or "https://" in t:
        return False
    if len(t) <= 2:
        return False
    return True


def preserve_ws(original: str, translated: str) -> str:
    start = re.match(r"^\s*", original).group(0)
    end = re.search(r"\s*$", original).group(0)
    return f"{start}{translated}{end}"


def tr(text: str) -> str:
    key = text.strip()
    if key in cache:
        out = cache[key]
    else:
        out = translator.translate(key)
        cache[key] = out
    return preserve_ws(text, out)


if soup.title and soup.title.string and should_translate_text(soup.title.string):
    soup.title.string.replace_with(tr(soup.title.string))

for tag in soup.find_all(True):
    for attr in ["content", "aria-label", "alt", "title", "placeholder"]:
        if tag.has_attr(attr):
            val = tag.get(attr, "")
            if isinstance(val, str) and should_translate_text(val):
                if not re.match(r"^(https?:|[\w-]+\.[\w.-]+/?)", val.strip()):
                    tag[attr] = tr(val).strip()

for node in soup.find_all(string=True):
    parent = node.parent.name if node.parent else ""
    if parent in {"script", "style"}:
        continue
    s = str(node)
    if should_translate_text(s):
        node.replace_with(tr(s))

with open(DST, "w", encoding="utf-8") as f:
    f.write(str(soup))

print(DST)
print("translated_strings", len(cache))
