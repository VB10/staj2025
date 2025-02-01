import requests
import json

# GitHub API'ya gönderilecek olan veriler
base_url = "https://api.github.com/repos/{owner}/{repo}"
owner = "vb10"
repo = "staj_2024"
comment_body = """
Merhaba arkadaşlar 
Sizler için yaklaşık 6 aydır çalıştım paylaştım elimden gelen tüm insanlara gelin bu repodan arkadaşlar var hazır bulun.
Hepinize erişemedim ama elimden gelenin çok daha fazlasına ulaştım staj sorununa yardım etmeye çalıştım.


İsterdim ki sektörde bu kadar yazılım şirketi var bu sorunu yaşamayın ama toz pembe sektör bir çok yayında anlattığım gibi.
Bir stajı yapmak ne bir işin başlangıcı yapamamak ise ne sonu. Önemli olan daima sizlersiniz

Hayat akıp giderken çok çalışıp başarılı olmaya emek vererek alın terinizle gitmeye devam edin.
Ben var olduğum sürece emek veren çalışkan arkadaşların yanında olmaya çalışacağım.
Bakarsınız bir gün daha büyürüm daha çok arkadaşa yardımcı olurum.


İşin özü hepinize gelecek dönemde başarılar diliyorum.
Umarım istediğiniz işi çalışma ortamını bulur ve mutlu güzel günler yaşarsınız.

Sevgirimle
vb10 (Repoyu akşam itibariyle sileceğim sizin bilgilerinizin elden geldiğince güvenliği için)
"""

# GitHub API'ya gönderilecek olan istek başlıkları
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "Bearer key"
}

# İlk sayfayı al
response = requests.get(base_url.format(owner=owner, repo=repo) + "/issues?state=open&per_page=100", headers=headers)
issues = response.json()

# Tüm sayfaları dolaşarak issue'ları al
while "next" in response.links:
    next_url = response.links["next"]["url"]
    response = requests.get(next_url, headers=headers)
    issues.extend(response.json())

# Her bir issue için yorum ekle
for issue in issues:
    issue_number = issue["number"]
    comment_url = base_url.format(owner=owner, repo=repo) + f"/issues/{issue_number}/comments"
    user = issue["user"]["login"]


    comment_text = f"{comment_body} @{user}"

    # Yorumu gönder
    comment_data = {
        "body": comment_text
    }

    # print(comment_text)
    response = requests.post(comment_url, headers=headers, data=json.dumps(comment_data))
    if response.status_code == 201:
        print(f"Yorum eklendi: Issue #{issue_number}")
    else:
        print(response.status_code)
        print(response.json())
        print(f"Yorum eklenirken hata oluştu: Issue #{issue_number}")