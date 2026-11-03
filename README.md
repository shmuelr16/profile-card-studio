# Profile Card Studio

[עברית](#עברית) · [English](#english)

---

<div dir="rtl">

## עברית

**Profile Card Studio** הוא סקיל ל-Claude, שהופך תמונת פורטרט אחת ורשימה של כל מה שבנית לשתי תמונות פרופיל ברמת מעצב: לינקדאין, פוסט, או כרטיס ביקור דיגיטלי.

### מה יוצא בסוף
- **גרסה מלאה** (`full.png`): בעברית, מימין לשמאל. שם, תואר, כלים, כרטיסי תפקידים וכל הפרויקטים לפי קטגוריות. הגובה גדל לפי כמות התוכן.
- **גרסה קצרה** (`short.png`): באנגלית, ביחס 4:5 (1080×1350). שם, תואר, כלים וכרטיסי תפקידים. מתאימה לפוסט.

### מה מיוחד בה
- **התמונה משולבת ברקע:** בלי עיגול פרופיל. הדמות נחתכת ונמסה לתוך הרקע הכהה.
- **צבעים טבעיים:** רק תיקון צבע עדין, אור דק בצבע המותג מאחור וגרעיניות קלה. הפנים לא נצבעות ולא מצוירות מחדש.
- **ניקוי קצוות:** מסירים את הרקע הישן שנשאר בין שערות הזקן והשיער, ומשחזרים את הצבע האמיתי של השיער בקצוות.
- **שם שלא מכסה את הפנים:** הגודל שלו מותאם אוטומטית.
- **בדיקות אוטומטיות:** חריגה מהרוחב, שם על הפנים, תוכן שעובר את הפוטר. בנוסף נוצרים חיתוכי תקריב לבדיקה בעין.

### התקנה

**ב-Claude Code** (מחשב או ענן):
```bash
git clone https://github.com/shmuelr16/profile-card-studio ~/.claude/skills/profile-card-studio
pip install --break-system-packages rembg pymatting opencv-python-headless pillow playwright
```
רוצים את הסקיל רק בפרויקט אחד? משכפלים ל-`.claude/skills/profile-card-studio` בתוך הפרויקט במקום ל-`~/.claude/skills`.

**ב-Claude.ai או באפליקציה:**
1. מורידים את הריפו כ-ZIP (‏Code ← Download ZIP), או מריצים:
   ```bash
   git clone https://github.com/shmuelr16/profile-card-studio
   zip -r profile-card-studio.zip profile-card-studio -x "*.git*"
   ```
2. נכנסים ל-Settings ← Capabilities ← Skills (צריך שהרצת קוד תהיה מופעלת).
3. לוחצים Upload skill ובוחרים את קובץ ה-ZIP.

### לעצלנים: פשוט מדביקים את זה ל-Claude
ב-Claude Code, מדביקים את הפרומט הזה והוא יעשה הכל לבד:
```text
תתקין לי את הסקיל מ-https://github.com/shmuelr16/profile-card-studio:
תשכפל אותו ל-~/.claude/skills/profile-card-studio, תתקין את כל התלויות
שמופיעות ב-README, ותוודא שהסקריפטים רצים.
אחרי זה תשתמש בסקיל ותכין לי תמונת פרופיל. התמונה שלי מצורפת.
```
ואחרי שהסקיל מותקן, מספיק לכתוב:
```text
תכין לי תמונת פרופיל לינקדאין עם הסקיל profile-card-studio. התמונה שלי מצורפת.
```

### איך משתמשים (ידנית)
```bash
pip install --break-system-packages rembg pymatting opencv-python-headless pillow playwright
python3 scripts/cutout.py photo.jpg out/cut.png --bg "#060B09" --accent "#3EFFA3"
cp examples/config.example.json config.json   # ממלאים את הפרטים
python3 scripts/build.py config.json out
python3 scripts/render.py out                 # full.png, short.png ודוח בדיקות
```

### כסקיל ב-Claude
`SKILL.md` מסביר ל-Claude את כל התהליך:
1. מחפש בזיכרון ובשיחות מה בנית. אם לא מוצא מספיק, שולח לך שאלון קצר.
2. שואל אם להוסיף את הלינק לאתר שלך.
3. בונה את שתי הגרסאות.
4. בודק את החיתוך בתקריב ושולח לך רק תוצאה נקייה.

### קובץ ההגדרות
כל השדות מופיעים ב-`examples/config.example.json`: שם, תואר, מותג, כלים, תפקידים, קטגוריות, משפט סיום, לינק, צבעים ופונטים. הפונטים נטענים מ-npm דרך `@fontsource`, כך שכל פונט של Google Fonts עובד לפי השם שלו.

</div>

---

## English

**Profile Card Studio** is a Claude skill that turns one portrait photo and a list of everything you built into two designer-grade profile images, for LinkedIn, a post, or a digital business card.

### What you get
- **Full version** (`full.png`): native language (Hebrew/RTL by default) with name, title, tools, role cards and every project grouped into sections. The page height grows with the content.
- **Short version** (`short.png`): English, 4:5 (1080×1350) with name, title, tools and role cards. Ready to post.

### What makes it different
- **The photo is part of the background:** no profile circle. The person is cut out and blended into the dark page.
- **Natural colours:** a gentle grade, a thin brand-colour rim light and subtle film grain. The face is never recoloured or redrawn.
- **Clean edges:** leftover backdrop between beard and hair strands is removed, and the true hair colour is recovered at the edges.
- **The name never covers the face:** its size is fitted automatically.
- **Automatic checks:** horizontal overflow, name over the face, and content past the footer. Close-up crops are also written for a visual review.

### Install

**Claude Code** (local or cloud):
```bash
git clone https://github.com/shmuelr16/profile-card-studio ~/.claude/skills/profile-card-studio
pip install --break-system-packages rembg pymatting opencv-python-headless pillow playwright
```
Want it in one project only? Clone into `.claude/skills/profile-card-studio` inside that project instead of `~/.claude/skills`.

**Claude.ai / desktop app:**
1. Download the repo as a ZIP (Code → Download ZIP), or run:
   ```bash
   git clone https://github.com/shmuelr16/profile-card-studio
   zip -r profile-card-studio.zip profile-card-studio -x "*.git*"
   ```
2. Open Settings → Capabilities → Skills (code execution must be on).
3. Click Upload skill and pick the ZIP.

### Lazy mode: just paste this to Claude
In Claude Code, paste this prompt and it does everything for you:
```text
Install the skill from https://github.com/shmuelr16/profile-card-studio:
clone it into ~/.claude/skills/profile-card-studio, install every dependency
listed in the README, and check that the scripts run.
Then use the skill to make my profile card. My photo is attached.
```
Once it's installed, this is enough:
```text
Make me a LinkedIn profile card with the profile-card-studio skill. My photo is attached.
```

### Manual usage
```bash
pip install --break-system-packages rembg pymatting opencv-python-headless pillow playwright
python3 scripts/cutout.py photo.jpg out/cut.png --bg "#060B09" --accent "#3EFFA3"
cp examples/config.example.json config.json   # fill in your details
python3 scripts/build.py config.json out
python3 scripts/render.py out                 # full.png, short.png + check report
```

### As a Claude skill
`SKILL.md` walks Claude through the whole flow:
1. It looks in memory and past chats for what you built, and sends you a short questionnaire if it can't find enough.
2. It asks whether to add your website link.
3. It builds both versions.
4. It inspects the cutout in close-up and only sends you a clean result.

### Config
Every field is in `examples/config.example.json`: name, title, brand, tools, roles, sections, tagline, link, colours and fonts. Fonts load from npm via `@fontsource`, so any Google Font works by its family name.

### Notes
- Segmentation uses rembg `isnet-general-use`. BiRefNet is sharper but needs more than 8 GB of RAM.
- Best input is a front-facing portrait on a plain background.
