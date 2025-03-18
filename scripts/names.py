import json
import os

# Seçilen başvuruların dosya yolu
selected_interns_file = "output/03mar/selected_interns.json"

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
