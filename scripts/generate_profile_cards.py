import json
import math
import subprocess
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
CARDS_DIR = ROOT / "assets" / "profile-cards"
README = ROOT / "README.md"

EXCLUDED = {
    "vault-plugin-secp256k1",
    "garage-notes",
    "abiturient_gui",
    "adboard",
    "cloudj",
}

GROUPS = {
    "Desktop": [
        "cursor-trail",
        "clipgloss-overlay",
        "securevol-windows",
    ],
    "Automation": [
        "tunnel-fox",
        "docx-pdf-bot",
        "ivbot",
    ],
    "Tools": [
        "tfs-cli",
        "go-import-cleaner",
        "openrouter-stt-proxy",
        "osu-beatmap-downloader",
        "osu-mp3-extracter",
        "osu-beatmaps-from-twitch-chat",
    ],
    "Games And Experiments": [
        "egks_app",
        "vk-console",
        "ahasuerus",
        "project768",
        "braid-flyhack",
        "asm_emulator",
    ],
}

LANG_COLORS = {
    "Batchfile": "#c1f12e",
    "C#": "#3fb950",
    "C++": "#f778ba",
    "Go": "#58a6ff",
    "Java": "#d29922",
    "PHP": "#a5a5ff",
    "PowerShell": "#79c0ff",
    "Python": "#79c0ff",
    "Shell": "#89e051",
}

STACK_LABELS = {
    "aiogram": "Aiogram",
    "android": "Android",
    "assembler": "Assembler",
    "azure-devops": "Azure DevOps",
    "debugger": "Debugger",
    "docker": "Docker",
    "emulator": "Emulator",
    "fastapi": "FastAPI",
    "godot-4": "Godot 4",
    "http-client": "HTTP",
    "jenkins": "Jenkins",
    "level-editor": "Editor",
    "libreoffice": "LibreOffice",
    "material-design": "Material",
    "memory-editing": "Memory",
    "minifilter": "Minifilter",
    "oauth2": "OAuth2",
    "opengl": "OpenGL",
    "openrouter": "OpenRouter",
    "osu-api": "osu! API",
    "raylib": "Raylib",
    "ssh-tunnel": "SSH Tunnel",
    "tkinter": "Tkinter",
    "trainer": "Trainer",
    "twitch": "Twitch",
    "v2ray": "V2Ray",
    "veracrypt": "VeraCrypt",
    "vk": "VK",
    "whisper": "Whisper",
    "wiql": "WIQL",
    "win32": "Win32",
    "wpf": "WPF",
}

STACK_PRIORITY = [
    "tkinter",
    "openrouter",
    "fastapi",
    "whisper",
    "wpf",
    "minifilter",
    "veracrypt",
    "android",
    "material-design",
    "aiogram",
    "libreoffice",
    "azure-devops",
    "wiql",
    "opengl",
    "win32",
    "godot-4",
    "raylib",
    "oauth2",
    "osu-api",
    "http-client",
    "vk",
    "docker",
    "jenkins",
    "ssh-tunnel",
    "v2ray",
    "assembler",
    "debugger",
    "emulator",
    "memory-editing",
    "trainer",
    "level-editor",
    "twitch",
]


def fetch_repos() -> dict[str, dict]:
    cmd = [
        "gh",
        "repo",
        "list",
        "nayutalienx",
        "--visibility",
        "public",
        "--limit",
        "200",
        "--json",
        "name,description,url,primaryLanguage,isFork,stargazerCount,forkCount,languages,repositoryTopics",
    ]
    raw = subprocess.check_output(cmd, cwd=ROOT, text=True)
    repos = json.loads(raw)
    return {repo["name"]: repo for repo in repos if repo["name"] not in EXCLUDED}


def trim_text(text: str, max_chars: int) -> str:
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "..."


def build_language_label(repo: dict, max_chars: int) -> tuple[str, str]:
    languages = sorted(
        repo.get("languages") or [],
        key=lambda item: item.get("size", 0),
        reverse=True,
    )
    names = [item["node"]["name"] for item in languages if item.get("node", {}).get("name")]
    if not names:
        primary = (repo.get("primaryLanguage") or {}).get("name") or "Other"
        return primary, primary

    head = names[:2]
    label = " / ".join(head)
    if len(names) > 2:
        label = f"{label} +{len(names) - 2}"
    return names[0], trim_text(label, max_chars)


def build_stack_label(repo: dict, max_chars: int) -> str:
    topics = {item["name"] for item in (repo.get("repositoryTopics") or []) if item.get("name")}
    labels = [STACK_LABELS[topic] for topic in STACK_PRIORITY if topic in topics]
    if not labels:
        return ""
    label = labels[0]
    if len(labels) > 1:
        combined = f"{labels[0]} / {labels[1]}"
        label = combined if len(combined) <= max_chars else label
    return trim_text(label, max_chars)


def build_card(repo: dict) -> str:
    width = 360
    height = 116
    bg = "#0d1117"
    border = "#30363d"
    title = "#58a6ff"
    text = "#c9d1d9"
    muted = "#8b949e"
    name = escape(repo["name"])
    url = escape(repo["url"])
    desc = trim_text(repo["description"] or "No description.", 110)
    desc_lines = wrap(desc, width=42)[:2]
    stars = repo.get("stargazerCount", 0)
    forks = repo.get("forkCount", 0)
    primary_language, language_label = build_language_label(
        repo, max_chars=18 if (stars > 0 or forks > 0) else 24
    )
    stack_label = build_stack_label(
        repo, max_chars=14 if (stars > 0 or forks > 0) else 18
    )
    lang_color = LANG_COLORS.get(primary_language, "#8b949e")

    desc_y = 46
    line_gap = 18
    desc_svg = []
    for i, line in enumerate(desc_lines):
        y = desc_y + i * line_gap
        desc_svg.append(
            f'<text x="18" y="{y}" fill="{text}" font-family="Segoe UI, Arial, sans-serif" '
            f'font-size="13">{escape(line)}</text>'
        )

    footer_y = height - 18
    footer_svg = [
        f'<circle cx="20" cy="{footer_y - 4}" r="5" fill="{lang_color}"/>',
        f'<text x="32" y="{footer_y}" fill="{muted}" font-family="Segoe UI, Arial, sans-serif" font-size="12">{escape(language_label)}</text>',
    ]

    next_x = 32 + len(language_label) * 6 + 18
    if stack_label:
        footer_svg.append(
            f'<text x="{next_x}" y="{footer_y}" fill="{muted}" font-family="Segoe UI, Arial, sans-serif" font-size="12">· {escape(stack_label)}</text>'
        )
        next_x += len(f"· {stack_label}") * 6 + 14
    if stars > 0:
        footer_svg.append(
            f'<text x="{next_x}" y="{footer_y}" fill="{muted}" font-family="Segoe UI Symbol, Segoe UI, Arial, sans-serif" font-size="12">★ {stars}</text>'
        )
        next_x += len(f"★ {stars}") * 7 + 14
    if forks > 0:
        footer_svg.append(
            f'<text x="{next_x}" y="{footer_y}" fill="{muted}" font-family="Segoe UI Symbol, Segoe UI, Arial, sans-serif" font-size="12">⑂ {forks}</text>'
        )

    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{bg}" stroke="{border}"/>',
            f'<text x="18" y="28" fill="{title}" font-family="Segoe UI, Arial, sans-serif" font-size="18" font-weight="600">{name}</text>',
            *desc_svg,
            *footer_svg,
            "</svg>",
        ]
    )


def write_cards(repos: dict[str, dict]) -> None:
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    for group_repos in GROUPS.values():
        for name in group_repos:
            repo = repos[name]
            (CARDS_DIR / f"{name}.svg").write_text(build_card(repo), encoding="utf-8")


def build_readme() -> str:
    lines = []
    for group, repos in GROUPS.items():
        lines.append(f"### {group}")
        lines.append("")
        row_count = math.ceil(len(repos) / 3)
        for row in range(row_count):
            chunk = repos[row * 3 : (row + 1) * 3]
            lines.append("<p>")
            for name in chunk:
                lines.append(
                    f'  <a href="https://github.com/nayutalienx/{name}"><img width="32%" src="./assets/profile-cards/{name}.svg" /></a>'
                )
            lines.append("</p>")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    repos = fetch_repos()
    write_cards(repos)
    README.write_text(build_readme(), encoding="utf-8")


if __name__ == "__main__":
    main()
