# Porsche Racing UI - Quick Start Guide

## ✅ Completed Setup

1. **Dependencies Installed:**
   - Tailwind CSS + PostCSS + Autoprefixer
   - @tailwindcss/typography
   - class-variance-authority + clsx + tailwind-merge
   - lucide-react (for icons)

2. **Configuration Files Created:**
   - `tailwind.config.js` - Porsche Racing theme tokens
   - `postcss.config.js` - PostCSS setup
   - `src/lib/utils.js` - cn() utility for class merging

3. **HTML Updated:**
   - Inter font loaded from Google Fonts
   - Dark mode class added to html element
   - Title changed to "LLM Council"

4. **Documentation:**
   - `PORSCHE_UI_SPEC.md` - Complete design system specification

---

## 🎯 Next Steps to Transform UI

### Option 1: Manual Implementation (You control everything)

**Step 1:** Replace `src/index.css` with:
```bash
# I'll provide the complete CSS in next message
```

**Step 2:** Use v0.dev or Cursor to generate components:
- Paste the **MASTER UI PROMPT** from your original message
- Include screenshots from racing.porsche.com
- Reference `PORSCHE_UI_SPEC.md` for exact tokens

**Step 3:** Replace existing components one by one:
- Start with `TopNav` component
- Then `LeftSidebar`  
- Then stage cards

### Option 2: I Can Generate Components for You

I can create the Porsche Racing-styled components right now:
1. TopNav component (brand + actions)
2. LeftSidebar (council members + conversations)
3. Stage cards (minimal tabs + content)
4. Input field (sharp, focused)
5. Model badges (uppercase, monochrome)

---

## 🎨 Design System Summary

**Colors:**
- Background: Deep graphite (#0f1014)
- Text: Cool white (#fafbfc)
- Accent: Electric blue (#1e8bf8)
- Borders: Subtle gray (#272b34)

**Typography:**
- Font: Inter (medium weight for headers)
- Headers: 2xl+ with tracking-tight
- Labels: xs uppercase with tracking-wider
- Body: sm/base compact

**Layout:**
- Sharp borders (0.125rem radius)
- Thin dividers
- Grid-driven
- Large negative space
- Fixed sidebar (280px)
- Top nav (64px)

**Motion:**
- 100ms transitions
- Linear easing
- Color + border changes only

---

## 📋 Current File Structure

```
frontend/
├── src/
│   ├── lib/
│   │   └── utils.js          ✅ Created
│   ├── components/           ⏳ To redesign
│   │   ├── Sidebar.jsx
│   │   ├── ChatInterface.jsx
│   │   ├── Stage1.jsx
│   │   ├── Stage2.jsx
│   │   └── Stage3.jsx
│   ├── App.jsx               ⏳ To restructure
│   ├── index.css             ⏳ To replace
│   └── main.jsx              ✅ No changes needed
├── index.html                ✅ Updated
├── tailwind.config.js        ✅ Created
├── postcss.config.js         ✅ Created
└── package.json              ✅ Updated
```

---

## 🚀 Choose Your Path

**Path A: "Generate everything for me"**
→ I'll create all components with Porsche Racing styling right now

**Path B: "I'll use v0.dev with the prompt"**
→ Use PORSCHE_UI_SPEC.md + MASTER UI PROMPT + racing.porsche.com screenshots

**Path C: "Show me one component first"**
→ I'll create TopNav as example, you adapt the rest

---

## 💡 Recommended Workflow

1. **Start with CSS foundation** (replace index.css)
2. **Create layout shell** (TopNav + Sidebar structure)
3. **Redesign one stage card** to perfection
4. **Scale pattern everywhere else**

This matches Porsche's philosophy: engineer one thing perfectly, then replicate.

---

## 🎬 Ready to Begin?

Tell me which path you want to take:
- "Generate all components"
- "Show me the TopNav component"
- "Just give me the updated index.css"
- "I'll use v0.dev, thanks for the setup"

Everything is configured and ready to transform your UI! 🏁
