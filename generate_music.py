import json
import urllib.request
from datetime import datetime

# GitHub GraphQL API query to fetch contribution calendar
USERNAME = "mimbres"
QUERY = """
query($userName: String!) {
  user(login: $userName) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            contributionLevel
            date
            weekday
          }
        }
      }
    }
  }
}
"""

def fetch_contributions():
    import os
    token = os.environ.get("GITHUB_TOKEN")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"userName": USERNAME}}).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def build_music_score_svg(weeks):
    # Flatten days and select recent 32 days for 4 bars (8 notes per bar)
    all_days = []
    for w in weeks:
        all_days.extend(w["contributionDays"])
    recent = all_days[-32:]
    
    # Treble staff Y-coordinates (E4 to F5)
    # Pitch mapping based on weekday (0: Sun -> C4/D4, up to 6: Sat -> B4/C5)
    pitch_y = [110, 102, 94, 86, 78, 70, 62]  # Y offsets for notes
    
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="180" viewBox="0 0 760 180">']
    svg.append('<rect width="100%" height="100%" fill="#0d1117" rx="10"/>')
    svg.append('<text x="30" y="32" fill="#58a6ff" font-family="monospace" font-size="14" font-weight="bold">Git Score: mimbres contribution melody</text>')
    
    # Draw 5 staff lines
    for i in range(5):
        y = 65 + i * 12
        svg.append(f'<line x1="30" y1="{y}" x2="730" y2="{y}" stroke="#30363d" stroke-width="1.5"/>')
        
    # Clef indicator & Bar lines
    svg.append('<text x="35" y="105" fill="#8b949e" font-family="serif" font-size="36">𝄞</text>')
    for bar in range(1, 4):
        bx = 70 + bar * 160
        svg.append(f'<line x1="{bx}" y1="65" x2="{bx}" y2="113" stroke="#484f58" stroke-width="1.5"/>')
    svg.append('<line x1="720" y1="65" x2="720" y2="113" stroke="#8b949e" stroke-width="3"/>')

    # Draw notes from contributions
    for idx, day in enumerate(recent):
        x = 90 + idx * 19.5
        weekday = day["weekday"]
        level = day["contributionLevel"]
        
        # Color based on commit intensity
        colors = {
            "NONE": "#484f58",
            "FIRST_QUARTILE": "#0e4429",
            "SECOND_QUARTILE": "#006d32",
            "THIRD_QUARTILE": "#26a641",
            "FOURTH_QUARTILE": "#39d353"
        }
        note_color = colors.get(level, "#484f58")
        y = pitch_y[weekday % len(pitch_y)]
        
        # Note head
        svg.append(f'<ellipse cx="{x}" cy="{y}" rx="5" ry="4" fill="{note_color}" transform="rotate(-20 {x} {y})"/>')
        # Note stem
        svg.append(f'<line x1="{x+4.5}" y1="{y}" x2="{x+4.5}" y2="{y-22}" stroke="{note_color}" stroke-width="1.5"/>')

    svg.append('</svg>')
    return "\n".join(svg)

def main():
    data = fetch_contributions()
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    svg_content = build_music_score_svg(weeks)
    
    with open("git-music-score.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

if __name__ == "__main__":
    main()
