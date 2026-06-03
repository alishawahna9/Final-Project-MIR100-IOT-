import json
import matplotlib.pyplot as plt

# 1. טעינת הקובץ מתיקיית ההורדות שלך
json_path = r"C:\Users\alish\Downloads\All connections (1).json"
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# שליפת מערך ההודעות המרכזי
messages = data[0]['messages']

# 2. סינון ושליפת נתונים עבור טמפרטורה (משלב את שני ה-Topics שקיימים בקובץ)
temp_msgs = [m for m in messages if m['topic'] in ['braude/team1/temperature', 'braude/team1/temp']]
temp_times = [m['createAt'] for m in temp_msgs]
temp_vals = [float(m['payload']) for m in temp_msgs]

# 3. סינון ושליפת נתונים עבור לחות
humidity_msgs = [m for m in messages if m['topic'] == 'braude/team1/humidity']
humidity_times = [m['createAt'] for m in humidity_msgs]
humidity_vals = [float(m['payload']) for m in humidity_msgs]

# 4. סינון ושליפת נתונים עבור לחץ אטמוספרי
pressure_msgs = [m for m in messages if m['topic'] == 'braude/team1/pressure']
pressure_times = [m['createAt'] for m in pressure_msgs]
pressure_vals = [float(m['payload']) for m in pressure_msgs]

# 5. יצירת לוח גרפים מפוצל (3 שורות, עמודה אחת)
fig, axs = plt.subplots(3, 1, figsize=(10, 12))

# --- גרף 1: טמפרטורה ---
axs[0].plot(temp_times, temp_vals, color='red', linewidth=1.5, label='Temperature')
axs[0].set_title('Team 1 - Temperature Over Time', fontsize=12, fontweight='bold')
axs[0].set_ylabel('Temperature (°C)')
axs[0].grid(True, linestyle='--', alpha=0.6)

# --- גרף 2: לחות ---
axs[1].plot(humidity_times, humidity_vals, color='blue', linewidth=1.5, label='Humidity')
axs[1].set_title('Team 1 - Humidity Over Time', fontsize=12, fontweight='bold')
axs[1].set_ylabel('Humidity (%)')
axs[1].grid(True, linestyle='--', alpha=0.6)

# --- גרף 3: לחץ אטמוספרי ---
axs[2].plot(pressure_times, pressure_vals, color='green', linewidth=1.5, label='Pressure')
axs[2].set_title('Team 1 - Atmospheric Pressure Over Time', fontsize=12, fontweight='bold')
axs[2].set_ylabel('Pressure (hPa)')
axs[2].grid(True, linestyle='--', alpha=0.6)

# 6. עיצוב וסידור צירי הזמן (X) כדי למנוע חפיפת טקסט
for ax in axs:
    ax.set_xlabel('Timestamp')
    # דילול אוטומטי של כמות התוויות על הציר כדי שלא יהיה עמוס
    ax.xaxis.set_major_locator(plt.MaxNLocator(8))
    # סיבוב הטקסט ב-30 מעלות לימין
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=9)

# מניעת צפיפות בין הגרפים
plt.tight_layout()

# 7. הצגת החלון עם כל הגרפים
plt.show()