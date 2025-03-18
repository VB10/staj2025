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

print(f"Starting with page: {page_number}, offset: {offset}, totalCount: {totalCount}")

# Fetch issues with pagination
selected_issues = []
max_retries = 3  # Maximum number of retries for failed requests
retry_count = 0

while len(selected_issues) < 50 and retry_count < max_retries:
    try:
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
            retry_count += 1
            continue
            
        issues = response.json()
        
        if not issues:
            print("No more issues available")
            break
            
        print(f"Page {page_number}: Found {len(issues)} issues")
        
        # Calculate how many issues we need from this page
        remaining_needed = 50 - len(selected_issues)
        
        # Handle the first page differently
        if page_number == (totalCount // per_page + 1):
            start_index = offset
            end_index = min(start_index + remaining_needed, len(issues))
            if start_index < len(issues):
                selected_issues.extend(issues[start_index:end_index])
        else:
            end_index = min(remaining_needed, len(issues))
            selected_issues.extend(issues[:end_index])
        
        print(f"Current total selected: {len(selected_issues)}")
        
        if len(selected_issues) >= 50:
            break
            
        page_number += 1
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        retry_count += 1
        continue

# If we still don't have 50 issues, try to get more from subsequent pages
if len(selected_issues) < 50:
    print(f"Warning: Only found {len(selected_issues)} issues. Trying to get more...")
    while len(selected_issues) < 50 and retry_count < max_retries:
        try:
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
                print(f"Error fetching additional issues: {response.status_code}")
                break
                
            issues = response.json()
            if not issues:
                break
                
            remaining = 50 - len(selected_issues)
            selected_issues.extend(issues[:remaining])
            print(f"Added {remaining} more issues from page {page_number}")
            page_number += 1
            
        except Exception as e:
            print(f"Error fetching additional issues: {str(e)}")
            break

print(f"Final total issues selected: {len(selected_issues)}")

if len(selected_issues) != 50:
    print(f"WARNING: Could not get exactly 50 issues. Only found {len(selected_issues)} issues.")
    print("Please check if there are enough open issues in the repository.")

# Print selected users before processing
print("\nSelected Users:")
print("-" * 50)
for idx, issue in enumerate(selected_issues, 1):
    print(f"{idx}. {issue['title']}")
print("-" * 50)

# Önceki last_selected dosyasından en son seçilen kişiyi ve sayfa bilgisini al
current_date = datetime.now().strftime("%d%b").lower()
output_dir = f"scripts/output/{current_date}"
os.makedirs(output_dir, exist_ok=True)

# Seçilen kişileri kaydetme
data_to_save = []
message_lines = []
duplicate_entries = []

# Daha önce eklenen isimleri takip etmek için set kullanımı
unique_names = set()

# Issue başlığını parse etme için regex deseni - updated to handle multiple durations and spaces
pattern = re.compile(r"^(.*?)\s*\[(.*?)\]\[(.*?)\]\[(.*?)\]\[(.*?)\]$")

# Calculate week number based on output folders
output_base_dir = "scripts/output"
existing_folders = [f for f in os.listdir(output_base_dir) if os.path.isdir(os.path.join(output_base_dir, f))]
week_number = len(existing_folders) + 1

# Updated LinkedIn intro message in Turkish with week number
linkedin_intro = (
    f"📢 **Staj 2025 - {week_number}. Hafta Değerlendirmesi** 📢\n\n"
    "🎯 Ekibinize yeni yetenekler katmak ister misiniz?\n"
    "💫 Bu hafta da birbirinden yetenekli stajyer adaylarımızı sizlerle buluşturuyoruz!\n\n"
    "✨ Öne Çıkan Özellikler:\n"
    "• Sigorta ve yasal yükümlülükler okul tarafından karşılanıyor\n"
    "• Hem uzaktan hem yüzyüze çalışma imkanı\n"
    "• Esnek staj süreleri\n\n"
    "👥 İşte bu haftanın parlayan adayları:"
)

message_lines.append(linkedin_intro)

print("\nProcessing issues:")
print("-" * 50)

for index, issue in enumerate(selected_issues):
    title = issue["title"]
    issue_url = issue["html_url"]
    
    # Clean the title before matching
    cleaned_title = (
        title.replace(" [", "[")
        .replace("[ ", "[")
        .replace(" ]", "]")
        .replace("] ", "]")
        .strip()
    )
    
    match = pattern.match(cleaned_title)
    if not match:
        print(f"Warning: Could not parse title format for: {title}")
        continue
    
    name, category, location, intern_type, duration = match.groups()
    
    # Clean all fields
    name = name.strip()
    category = ",".join(item.strip() for item in category.split(","))
    location = ",".join(item.strip() for item in location.split(","))
    intern_type = intern_type.strip()
    duration = ",".join(item.strip() for item in duration.split(","))
    
    if name in unique_names:
        print(f"Duplicate name found: {name}")
        duplicate_entries.append({
            "name": name,
            "issue_url": issue_url,
            "duration": duration,
            "location": location,
            "intern_type": intern_type,
            "category": category
        })
        continue
    
    unique_names.add(name)
    
    # Add to data_to_save regardless of duplicates
    data_to_save.append({
        "id": issue["id"],
        "name": name,
        "issue_url": issue_url,
        "duration": duration,
        "location": location,
        "intern_type": intern_type,
        "category": category
    })
    
    # Format message for LinkedIn
    formatted_message = (
        f"- {name} [💻 {category}]"
    )
    message_lines.append(formatted_message)

print(f"\nTotal records processed: {len(selected_issues)}")
print(f"Records to be saved: {len(data_to_save)}")
print(f"Duplicate entries found: {len(duplicate_entries)}")

# Son seçilen kişiyi belirleme
if data_to_save:
    last_selected = data_to_save[-1]
    # Update last selected intern with new totalCount
    new_total_count = totalCount + len(selected_issues)
    last_selected_data = {
        "id": selected_issues[-1]["id"],
        "name": last_selected["name"],
        "issue_url": last_selected["issue_url"],
        "duration": last_selected["duration"],
        "location": last_selected["location"],
        "intern_type": last_selected["intern_type"],
        "category": last_selected["category"],
        "page": page_number - 1,
        "folderName": current_date,
        "totalCount": new_total_count
    }

    # Write files
    with open(f"{output_dir}/selected_interns.json", "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    with open(last_selected_file, "w", encoding="utf-8") as f:
        json.dump(last_selected_data, f, ensure_ascii=False, indent=4)

    with open(f"{output_dir}/intern_message.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(message_lines))

    with open(f"{output_dir}/duplicate_entries.json", "w", encoding="utf-8") as f:
        json.dump(duplicate_entries, f, ensure_ascii=False, indent=4)

    print(f"\nFiles saved successfully in {output_dir}")
    print(f"Total records saved: {len(data_to_save)}")
else:
    print("\nNo records to save!")
