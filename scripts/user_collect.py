import requests
import json
from datetime import datetime
import re
import os


github_repo = "VB10/staj2025"
github_api_url = f"https://api.github.com/repos/{github_repo}/issues?sort=created&direction=asc"
# Import token from config file
try:
    from config import GITHUB_TOKEN
    github_headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }
except ImportError:
    print("config.py dosyası bulunamadı! Lütfen config.py dosyasını oluşturun ve GitHub token'ını ekleyin.")
    exit()

# Read last_selected.json to get previous data
last_selected_file = "scripts/output/last_selected.json"
if os.path.exists(last_selected_file) and os.path.getsize(last_selected_file) > 0:
    with open(last_selected_file, "r", encoding="utf-8") as f:
        try:
            last_selected = json.load(f)
            totalCount = last_selected.get("totalCount", 0)
            last_folder = last_selected.get("folderName")
        except json.JSONDecodeError:
            last_selected = {}
            totalCount = 0
            last_folder = None
else:
    last_selected = {}
    totalCount = 0
    last_folder = None

# Calculate page and offset
per_page = 30
page_number = totalCount // per_page + 1
offset = totalCount % per_page

# Fetch issues with pagination
selected_issues = []
while len(selected_issues) < 15:
    response = requests.get(
        github_api_url,
        headers=github_headers,
        params={
            "state": "open",
            "per_page": per_page,
            "page": page_number
        }
    )
    
    if response.status_code != 200:
        print(f"Error fetching issues: {response.status_code}")
        break
        
    issues = response.json()
    if not issues:
        break  # No more issues available
        
    # Skip offset only on the first page
    start_index = offset if page_number == (totalCount // per_page + 1) else 0
    selected_issues.extend(issues[start_index:start_index + (15 - len(selected_issues))])
    page_number += 1

# Önceki last_selected dosyasından en son seçilen kişiyi ve sayfa bilgisini al
current_date = datetime.now().strftime("%d%b").lower()
output_dir = f"scripts/output/{current_date}"
os.makedirs(output_dir, exist_ok=True)

# Önceki seçilen kullanıcı sayısını al
previous_selected_count = 0

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
            "category": category
        })
        continue  # Aynı isim tekrar geldiyse eklemiyoruz
    
    unique_names.add(name)
    
    # Mesajı oluşturma (her alanı kutu içine alma, ancak kısaltılmış formatta)
    formatted_message = (
        f"- {name} [📅 {duration}] [💻 {category}] [📍 {location}] [⚡ {intern_type}] | [Başvuru]({issue_url})"
    )
    
    message_lines.append(formatted_message)
    
    data_to_save.append({
        "id": issue["id"],  # Add issue ID for tracking
        "name": name,
        "issue_url": issue_url,
        "duration": duration,
        "location": location,
        "intern_type": intern_type,
        "category": category
    })

# Son seçilen kişiyi belirleme
last_selected = data_to_save[-1] if data_to_save else {}

# Update last selected intern with new totalCount
new_total_count = totalCount + len(selected_issues)
last_selected_data = {
    "id": selected_issues[-1]["id"],
    "name": selected_issues[-1]["title"].split("|")[0].strip(),
    "issue_url": selected_issues[-1]["html_url"],
    "duration": duration,
    "location": location,
    "intern_type": intern_type,
    "category": category,
    "page": page_number - 1,  # Last page we fetched
    "folderName": current_date,
    "totalCount": new_total_count
}

# Dosyaya yazma
with open(f"{output_dir}/selected_interns.json", "w", encoding="utf-8") as f:
    json.dump(data_to_save, f, ensure_ascii=False, indent=4)

with open(last_selected_file, "w", encoding="utf-8") as f:
    json.dump(last_selected_data, f, ensure_ascii=False, indent=4)

with open(f"{output_dir}/intern_message.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(message_lines))

with open(f"{output_dir}/duplicate_entries.json", "w", encoding="utf-8") as f:
    json.dump(duplicate_entries, f, ensure_ascii=False, indent=4)

print(f"Seçilen başvurular {output_dir} klasörüne kaydedildi ve mesaj dosyası oluşturuldu.")
print(f"Tekrar eden isimler {output_dir}/duplicate_entries.json dosyasına kaydedildi.")
