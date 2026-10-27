import gc
import os
import sys
import threading
from collections import OrderedDict

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
os.environ.update({
    "HOME": DATA,
    "XDG_DATA_HOME": os.path.join(DATA, "share"),
    "XDG_CACHE_HOME": os.path.join(DATA, "cache"),
    "XDG_CONFIG_HOME": os.path.join(DATA, "config"),
    "ARGOS_PACKAGES_DIR": os.path.join(DATA, "share", "argos-translate", "packages"),
    "ARGOS_DEVICE_TYPE": "cpu",
    "HF_HUB_OFFLINE": "1",
})

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import webview
from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0

LANGUAGE_NAMES = {
    "ar": "ערבית", "az": "אזרית", "bg": "בולגרית", "bn": "בנגלית", "ca": "קטלאנית",
    "cs": "צ'כית", "da": "דנית", "de": "גרמנית", "el": "יוונית", "en": "אנגלית",
    "eo": "אספרנטו", "es": "ספרדית", "et": "אסטונית", "eu": "בסקית", "fa": "פרסית",
    "fi": "פינית", "fr": "צרפתית", "ga": "אירית", "gl": "גליסית", "he": "עברית",
    "hi": "הינדי", "hu": "הונגרית", "id": "אינדונזית", "it": "איטלקית", "ja": "יפנית",
    "ko": "קוריאנית", "ky": "קירגיזית", "lt": "ליטאית", "lv": "לטבית", "ms": "מלאית",
    "nb": "נורווגית", "nl": "הולנדית", "pb": "פורטוגזית (ברזיל)", "pl": "פולנית",
    "pt": "פורטוגזית", "ro": "רומנית", "ru": "רוסית", "sk": "סלובקית", "sl": "סלובנית",
    "sq": "אלבנית", "sv": "שוודית", "sw": "סווהילית", "th": "תאית", "tl": "טגלוג",
    "tr": "טורקית", "uk": "אוקראינית", "ur": "אורדו", "vi": "וייטנאמית",
    "zh": "סינית", "zt": "סינית (מסורתית)",
}

HTML = r"""<!doctype html>
<html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
body{margin:0;font-family:"Segoe UI",Arial,sans-serif;background:#f1f3f4;color:#202124}
header{background:#fff;padding:14px 24px;font-size:24px;color:#5f6368;border-bottom:1px solid #dadce0}
header b{color:#1a73e8;font-weight:600}
main{max-width:1200px;margin:24px auto;padding:0 16px}
.bar{display:flex;align-items:center;gap:12px;margin-bottom:12px}
select{flex:1;padding:12px;font-size:17px;border:1px solid #dadce0;border-radius:8px;background:#fff;color:#1a73e8;font-weight:600;font-family:inherit}
#swap{border:1px solid #dadce0;background:#fff;font-size:22px;cursor:pointer;color:#5f6368;width:48px;height:48px;border-radius:50%}
#swap:hover{background:#e8eaed}
.panes{display:flex;gap:16px}
.pane{flex:1;position:relative;background:#fff;border:1px solid #dadce0;border-radius:8px;min-height:320px}
.pane.out{background:#f8f9fa}
textarea{width:100%;height:100%;min-height:320px;border:none;resize:none;padding:18px 18px 52px;font-size:24px;font-family:inherit;background:transparent;outline:none;color:inherit}
.tools{position:absolute;bottom:10px;right:14px;left:14px;display:flex;justify-content:space-between;align-items:center;font-size:14px;color:#5f6368}
.tools button{border:1px solid #dadce0;background:#fff;cursor:pointer;color:#1a73e8;font-size:15px;padding:6px 16px;border-radius:18px;font-family:inherit}
.tools button:hover{background:#e8f0fe}
#status{font-size:15px;color:#5f6368;margin-top:12px;min-height:20px}
@media (max-width:760px){.panes{flex-direction:column}}
</style></head><body>
<header><b>תרגום</b> אופליין</header>
<main>
<div class="bar">
<select id="src"></select>
<button id="swap" title="החלפת שפות">&#8644;</button>
<select id="tgt"></select>
</div>
<div class="panes">
<div class="pane"><textarea id="in" dir="auto" placeholder="הקלידו או הדביקו כאן טקסט" autofocus></textarea>
<div class="tools"><span id="count">0 / 5000</span><button id="clear">ניקוי</button></div></div>
<div class="pane out"><textarea id="out" dir="auto" placeholder="התרגום יופיע כאן" readonly></textarea>
<div class="tools"><span></span><button id="copy">העתקה</button></div></div>
</div>
<div id="status">טוען שפות...</div>
</main>
<script>
const $ = id => document.getElementById(id);
let timer = null, seq = 0, names = {};
function fill(langs) {
  langs.forEach(l => names[l.code] = l.name);
  const opts = langs.map(l => `<option value="${l.code}">${l.name}</option>`).join("");
  $("src").innerHTML = '<option value="auto">זיהוי אוטומטי</option>' + opts;
  $("tgt").innerHTML = opts;
  $("src").value = names.he ? "he" : "auto";
  $("tgt").value = "en";
  $("status").textContent = "";
}
async function run() {
  const text = $("in").value, id = ++seq;
  $("count").textContent = text.length + " / 5000";
  if (!text.trim()) { $("out").value = ""; $("status").textContent = ""; return; }
  $("status").textContent = "מתרגם...";
  const r = await pywebview.api.translate(text, $("src").value, $("tgt").value);
  if (id !== seq) return;
  $("out").value = r.text;
  $("status").textContent = r.error ? r.error : (r.detected ? "השפה שזוהתה: " + (names[r.detected] || r.detected) : "");
}
function schedule() { clearTimeout(timer); timer = setTimeout(run, 400); }
$("in").addEventListener("input", schedule);
$("src").addEventListener("change", run);
$("tgt").addEventListener("change", run);
$("swap").onclick = () => {
  if ($("src").value === "auto") return;
  [$("src").value, $("tgt").value] = [$("tgt").value, $("src").value];
  $("in").value = $("out").value; run();
};
$("clear").onclick = () => { $("in").value = ""; run(); $("in").focus(); };
$("copy").onclick = () => { navigator.clipboard.writeText($("out").value); $("copy").textContent = "הועתק ✓"; setTimeout(() => $("copy").textContent = "העתקה", 1200); };
$("in").maxLength = 5000;
window.addEventListener("pywebviewready", async () => fill(await pywebview.api.languages()));
</script></body></html>"""


MAX_LOADED_MODELS = 6


def package_models(translation):
    from argostranslate.translate import CachedTranslation, CompositeTranslation, PackageTranslation
    if isinstance(translation, CachedTranslation):
        return package_models(translation.underlying)
    if isinstance(translation, CompositeTranslation):
        return package_models(translation.t1) + package_models(translation.t2)
    if isinstance(translation, PackageTranslation):
        return [translation]
    return []


class Api:
    def __init__(self):
        self._lock = threading.Lock()
        self._langs = None
        self._loaded = OrderedDict()

    def _touch(self, translation):
        for model in package_models(translation):
            self._loaded.pop(id(model), None)
            self._loaded[id(model)] = model
        evicted = False
        while len(self._loaded) > MAX_LOADED_MODELS:
            _, model = self._loaded.popitem(last=False)
            model.translator = None
            evicted = True
        if evicted:
            gc.collect()

    def _load(self):
        if self._langs is None:
            from argostranslate import translate
            self._langs = {l.code: l for l in translate.get_installed_languages()}
        return self._langs

    def languages(self):
        with self._lock:
            langs = self._load()
        items = [{"code": c, "name": LANGUAGE_NAMES.get(c, l.name)} for c, l in langs.items()]
        return sorted(items, key=lambda x: x["name"])

    def translate(self, text, source, target):
        with self._lock:
            langs = self._load()
            detected = None
            if source == "auto":
                try:
                    detected = detect(text)
                except Exception:
                    detected = "en"
                source = {"iw": "he", "zh-cn": "zh", "zh-tw": "zt", "no": "nb"}.get(detected, detected)
                if source not in langs:
                    source = "en"
                detected = source
            if source == target:
                return {"text": text, "detected": detected}
            translation = langs[source].get_translation(langs[target])
            if translation is None:
                return {"text": "", "error": "אין תרגום בין שתי השפות האלה."}
            result = translation.translate(text)
            self._touch(translation)
            return {"text": result, "detected": detected}


TITLE = "תרגום אופליין"
ICON = os.path.join(ROOT, "icon.ico")


def set_window_icon():
    import ctypes
    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW(None, TITLE)
    if not hwnd or not os.path.exists(ICON):
        return
    for size, which in ((32, 1), (16, 0)):
        icon = user32.LoadImageW(None, ICON, 1, size, size, 0x10)
        user32.SendMessageW(hwnd, 0x80, which, icon)


def main():
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ariel600.TranslateOffline")
    window = webview.create_window(TITLE, html=HTML, js_api=Api(), width=1200, height=760, min_size=(700, 500))
    window.events.shown += set_window_icon
    webview.start()


if __name__ == "__main__":
    main()
