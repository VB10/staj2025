import requests
import json
from datetime import datetime
import re
import os

github_repo = "VB10/staj2025"
github_api_url = f"https://api.github.com/repos/{github_repo}/issues?sort=created&direction=asc"
github_headers = {"Accept": "application/vnd.github.v3+json"}

# GitHub Issues'tan verileri çekme
response = requests.get(github_api_url, headers=github_headers)
issues = response.json()

# Pagination ayarları (25'li gruplar halinde çekildiğini varsayıyoruz)
issues_per_page = 20

# Önceki last_selected dosyasından en son seçilen kişiyi ve sayfa bilgisini al
current_date = datetime.now().strftime("%d%b").lower()
output_dir = f"output/{current_date}"
os.makedirs(output_dir, exist_ok=True)

last_selected_file = "output/last_selected.json"
if os.path.exists(last_selected_file) and os.path.getsize(last_selected_file) > 0:
    with open(last_selected_file, "r", encoding="utf-8") as f:
        try:
            last_selected = json.load(f)
            last_selected_index = next((i for i, issue in enumerate(issues) if issue["title"].startswith(last_selected.get("name", ""))), -1)
            start_index = last_selected_index + 1 if last_selected_index >= 0 else 0
        except json.JSONDecodeError:
            last_selected = {}
            start_index = 0
else:
    last_selected = {}
    start_index = 0

# İlk 20 kişiyi seçme
selected_issues = issues[start_index:start_index + issues_per_page]

# Seçilen kişileri kaydetme
data_to_save = []
message_lines = []
duplicate_entries = []

# Daha önce eklenen isimleri takip etmek için set kullanımı
unique_names = set()

# Issue başlığını parse etme için regex deseni
pattern = re.compile(r"^(.*?) \[(.*?)\]\[(.*?)\]\[(.*?)\]\[(.*?)\]$")

# LinkedIn gönderisi için giriş metni
linkedin_intro = (
    "📢 **Staj 2025 Reposunda ekibinizde çalışmaya hazır, kariyerine yön vermek isteyen yetenekli stajyerler burada!** 📢\n\n"
    "🎯 Sigortaları okulları tarafından karşılanıyor, hedefleri büyük!\n"
    "💡 Onlara bir şans verin, birlikte harika işler başarabilirsiniz.\n\n"
    "🔗 İşte bu haftanın adayları:"
)

message_lines.append(linkedin_intro)

for index, issue in enumerate(selected_issues):
    title = issue["title"]
    issue_url = issue["html_url"]
    
    match = pattern.match(title)
    if not match:
        continue  # Eğer format uygun değilse atla
    
    name, category, location, intern_type, duration = match.groups()
    
    if name in unique_names:
        duplicate_entries.append({
            "name": name,
            "issue_url": issue_url,
            "duration": duration,
            "location": location,
            "intern_type": intern_type,
            "category": category,
            "page": (start_index // issues_per_page) + 1  # Pagination sayfasını hesapla
        })
        continue  # Aynı isim tekrar geldiyse eklemiyoruz
    
    unique_names.add(name)
    
    # Mesajı oluşturma (her alanı kutu içine alma, ancak kısaltılmış formatta)
    formatted_message = (
        f"- {name} [📅 {duration}] [💻 {category}] [📍 {location}] [⚡ {intern_type}] | [Başvuru]({issue_url})"
    )
    
    message_lines.append(formatted_message)
    
    data_to_save.append({
        "name": name,
        "issue_url": issue_url,
        "duration": duration,
        "location": location,
        "intern_type": intern_type,
        "category": category,
        "page": (start_index // issues_per_page) + 1
    })

# Son seçilen kişiyi belirleme
last_selected = data_to_save[-1] if data_to_save else {}

# Dosyaya yazma
with open(f"{output_dir}/selected_interns.json", "w", encoding="utf-8") as f:
    json.dump(data_to_save, f, ensure_ascii=False, indent=4)

with open(last_selected_file, "w", encoding="utf-8") as f:
    json.dump(last_selected, f, ensure_ascii=False, indent=4)

with open(f"{output_dir}/intern_message.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(message_lines))

with open(f"{output_dir}/duplicate_entries.json", "w", encoding="utf-8") as f:
    json.dump(duplicate_entries, f, ensure_ascii=False, indent=4)

print(f"Seçilen başvurular {output_dir} klasörüne kaydedildi ve mesaj dosyası oluşturuldu.")
print(f"Tekrar eden isimler {output_dir}/duplicate_entries.json dosyasına kaydedildi.")
