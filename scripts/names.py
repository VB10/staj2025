import json
import os
from datetime import datetime
current_date = datetime.now().strftime("%d%b").lower()
# Seçilen başvuruların dosya yolu
selected_interns_file = f"scripts/output/{current_date}/selected_interns.json"

# Dosya kontrolü
if not os.path.exists(selected_interns_file):
    print("Hata: selected_interns.json dosyası bulunamadı!")
    exit()

# Dosyayı oku
with open(selected_interns_file, "r", encoding="utf-8") as f:
    selected_interns = json.load(f)

# İsimleri listele
for intern in selected_interns:
    print(intern["name"])
