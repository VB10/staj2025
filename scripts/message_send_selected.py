import requests
import json
import os
from datetime import datetime

# GitHub API ayarları
github_repo = "VB10/staj2025"
github_api_url = f"https://api.github.com/repos/{github_repo}/issues"

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

# LinkedIn paylaşım linki (statik olarak tanımlanıyor)
linkedin_post_url = "https://www.linkedin.com/posts/veli-bacik-345978a9_staj-2025-3-hafta-bu-hafta-activity-7302304963609686016-RdW_?utm_source=share&utm_medium=member_desktop&rcm=ACoAABcaKuUBuJwj2vB7GRk2JRtQ1navi1AEMwU"

# En son seçilenlerin bulunduğu dosyanın yolu
current_date = datetime.now().strftime("%d%b").lower()
output_dir = f"scripts/output/{current_date}"
selected_issues_file = f"{output_dir}/selected_interns.json"

# Dosya varsa yükle
if not os.path.exists(selected_issues_file):
    print(f"Seçilen başvurular dosyası bulunamadı! {selected_issues_file}")
    exit()

with open(selected_issues_file, "r", encoding="utf-8") as f:
    selected_issues = json.load(f)

# GitHub yorumlarını ekleyelim
for issue in selected_issues:
    issue_number = issue["issue_url"].split("/")[-1]
    comment_body = {
        "body": f"Selam {issue['name']}! 🎉\n\n"
                 f"Başvurularını LinkedIn'de paylaştık! \n"
                 f"Göz atmak için tıklayabilirsin: [LinkedIn Postu]({linkedin_post_url}) 📢\n\n"
                 f"Başarılar dileriz! 🚀"
    }
    
    response = requests.post(f"{github_api_url}/{issue_number}/comments", 
                             headers=github_headers, 
                             json=comment_body)
    
    if response.status_code == 201:
        print(f"Başarıyla yorum yapıldı: {issue['issue_url']}")
    else:
        print(f"Yorum eklenirken hata oluştu: {issue['issue_url']} - {response.status_code}")
