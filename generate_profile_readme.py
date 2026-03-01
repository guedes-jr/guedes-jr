import os
import requests
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

README_FILE = "README.md"

HEADERS = {
    "Authorization": f"token {TOKEN}"
}

API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"

LANG_ICONS = {
    "Python": "🐍",
    "TypeScript": "🟦",
    "JavaScript": "🟨",
    "HTML": "🌐",
    "CSS": "🎨",
    "Go": "🐹",
    "C#": "⚙️",
    "Vue": "💚",
    "Outros": "📦"
}

def fetch_repositories():
    repos = []
    page = 1

    while True:
        response = requests.get(
            f"{API_URL}&page={page}",
            headers=HEADERS
        )

        data = response.json()

        if not data:
            break

        for repo in data:
            if repo["fork"]:
                continue
                
            if repo["name"].lower() == USERNAME.lower():
                continue

            repos.append({
                "name": repo["name"],
                "description": repo["description"],
                "url": repo["html_url"],
                "language": repo["language"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "pushed_at": repo["pushed_at"]
            })

        page += 1

    return repos

def get_featured_projects(repos, limit=6):
    return sorted(
        repos,
        key=lambda r: r["pushed_at"],
        reverse=True
    )[:limit]

def group_by_language(repos):
    grouped = defaultdict(list)

    for repo in repos:
        lang = repo["language"] or "Outros"
        grouped[lang].append(repo)

    return dict(sorted(grouped.items()))

def build_card(repo):

    desc = repo["description"] or "Sem descrição disponível"
    lang = repo["language"] or "N/A"
    icon = LANG_ICONS.get(lang, "📦")

    return f"""
<td width="33%" valign="top">

### [{repo['name']}]({repo['url']})

{desc}

⭐ {repo['stars']} • 🍴 {repo['forks']} {icon} {lang}

</td>
"""

def build_featured_section(featured):

    cards = []

    for repo in featured:

        desc = repo["description"] or "Sem descrição disponível"
        lang = repo["language"] or "N/A"

        card = f"""
<td width="33%" valign="top">

<div style="
border-radius:12px;
padding:16px;
border:1px solid #30363d;
background-color:#0d1117;
height:180px;
">

<h3>
<a href="{repo['url']}"
style="color:#58a6ff;text-decoration:none;">
{repo['name']}
</a>
</h3>

<p style="color:#8b949e;font-size:14px;">
{desc}
</p>

<p style="color:#8b949e;font-size:12px;">
⭐ {repo['stars']} • 🍴 {repo['forks']} • 🧠 {lang}
</p>

</div>

</td>
"""
        cards.append(card)

    rows = []
    for i in range(0, len(cards), 3):
        rows.append("<tr>" + "".join(cards[i:i+3]) + "</tr>")

    table = "\n".join(rows)

    return f"""
<table width="100%">
{table}
</table>
"""

def build_projects_section(grouped):

    html = ""

    for lang, repos in grouped.items():
        icon = LANG_ICONS.get(lang, "📦")
        repos_sorted = sorted(
            repos,
            key=lambda r: r["stars"],
            reverse=True
        )

        html += f"""
<details>
<summary><b>{icon} {lang} ({len(repos_sorted)} projetos)</b></summary>

<br>
"""

        for r in repos_sorted:
            html += f"""
- **[{r['name']}]({r['url']})**
  - {r['description'] or 'Sem descrição'}
"""

        html += "\n</details>\n"

    return html


def replace_section(content, start, end, new_data):

    start_index = content.find(start)
    end_index = content.find(end)

    if start_index == -1 or end_index == -1:
        print(f"⚠️ Marcadores não encontrados: {start}")
        return content

    end_index += len(end)

    return (
        content[:start_index]
        + start
        + "\n"
        + new_data
        + "\n"
        + content[end_index - len(end):]
    )

def generate_readme():

    repos = fetch_repositories()

    featured_html = build_featured_section(
        get_featured_projects(repos)
    )

    projects_html = build_projects_section(
        group_by_language(repos)
    )

    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    readme = replace_section(
        readme,
        "<!-- AUTO-GENERATED:FEATURED_PROJECTS_START -->",
        "<!-- AUTO-GENERATED:FEATURED_PROJECTS_END -->",
        featured_html
    )

    readme = replace_section(
        readme,
        "<!-- AUTO-GENERATED:PROJECTS_START -->",
        "<!-- AUTO-GENERATED:PROJECTS_END -->",
        projects_html
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme)

    print("✅ README atualizado com sucesso!")


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    generate_readme()