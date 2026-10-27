import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from languages import DEFAULT_LANGUAGES, LANGUAGE_NAMES

PACKAGES = r"data\share\argos-translate\packages"


def main():
    source_dir, output = sys.argv[1], sys.argv[2]
    packages_dir = os.path.join(source_dir, PACKAGES)
    packages = []
    for name in sorted(os.listdir(packages_dir)):
        with open(os.path.join(packages_dir, name, "metadata.json"), encoding="utf-8") as f:
            meta = json.load(f)
        packages.append((name, meta["from_code"], meta["to_code"]))

    codes = sorted({c for _, a, b in packages for c in (a, b) if c != "en"}, key=lambda c: LANGUAGE_NAMES.get(c, c))

    lines = ["[Types]",
             'Name: "custom"; Description: "בחירת שפות"; Flags: iscustom',
             'Name: "full"; Description: "כל השפות"',
             "",
             "[Components]",
             'Name: "lang_en"; Description: "אנגלית (חובה)"; Types: full custom; Flags: fixed']
    for code in codes:
        types = "full custom" if code in DEFAULT_LANGUAGES else "full"
        lines.append(f'Name: "lang_{code}"; Description: "{LANGUAGE_NAMES.get(code, code)}"; Types: {types}')

    lines += ["", "[Files]"]
    for name, a, b in packages:
        others = [c for c in (a, b) if c != "en"]
        components = " and ".join(f"lang_{c}" for c in others) or "lang_en"
        lines.append(f'Source: "{{#SourceDir}}\\{PACKAGES}\\{name}\\*"; DestDir: "{{app}}\\{PACKAGES}\\{name}"; '
                     f"Flags: ignoreversion recursesubdirs createallsubdirs; Components: {components}")

    with open(output, "w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{len(codes) + 1} languages, {len(packages)} packages -> {output}")


if __name__ == "__main__":
    main()
