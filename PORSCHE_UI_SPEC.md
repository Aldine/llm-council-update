# Porsche Racing-Inspired UI Transformation
## LLM Council Interface Redesign

---

## Implementation Status

✅ Dependencies installed:
- Tailwind CSS
- @tailwindcss/typography  
- class-variance-authority
- clsx
- tailwind-merge
- lucide-react

⏳ To implement:
1. Theme configuration
2. Component library setup
3. Layout restructure
4. Component redesign

---

## Design System Token Reference

### Color Palette (Dark Mode First)

```css
/* Porsche Racing - Industrial Graphite */
--background: 220 13% 6%;        /* Deep graphite black #0f1014 */
--foreground: 210 8% 98%;        /* Cool white #fafbfc */

--card: 220 12% 8%;              /* Elevated surface #13151a */
--border: 220 10% 18%;           /* Thin dividers #272b34 */

--primary: 0 0% 100%;            /* Pure white for CTAs */
--accent: 210 90% 55%;           /* Porsche electric blue #1e8bf8 */

--muted: 220 10% 15%;            /* Disabled states */
--muted-foreground: 210 8% 50%;  /* Secondary text */
```

### Typography Scale

```css
Font Family: Inter (primary), SF Pro (fallback)
 
h1: 2.25rem / 2.5rem   | font-medium | tracking-tight
h2: 1.875rem / 2.25rem | font-medium | tracking-tight  
h3: 1.5rem / 2rem      | font-medium | tracking-tight

Body: 1rem / 1.5rem    | font-normal
Small: 0.875rem / 1.25rem
Labels: 0.75rem / 1rem | UPPERCASE | tracking-wider
```

### Spacing System

```
Tight: 0.5rem (8px)
Base: 1rem (16px)
Medium: 1.5rem (24px)
Large: 2rem (32px)
XL: 3rem (48px)
```

### Border Radius

```css
--radius: 0.125rem;  /* 2px - Sharp, minimal */
```

---

## Component Architecture

### 1. Top Navigation Bar

**Layout:** Fixed top, full width
**Height:** 64px
**Structure:**
- Left: Brand logo + wordmark
- Right: User actions (command palette trigger, settings)

```jsx
<nav className="fixed top-0 w-full h-16 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
  <div className="flex items-center justify-between h-full px-6">
    <div className="flex items-center gap-4">
      <span className="text-xl font-medium tracking-tight">LLM COUNCIL</span>
    </div>
    <div className="flex items-center gap-2">
      {/* Command palette, settings */}
    </div>
  </div>
</nav>
```

---

### 2. Left Sidebar

**Width:** 280px (fixed)
**Purpose:** Model selection, conversation history
**Style:** Minimal chrome, thin dividers

```jsx
<aside className="fixed left-0 top-16 bottom-0 w-[280px] border-r border-border bg-card/50">
  <div className="flex flex-col h-full">
    {/* Council Members section */}
    <div className="p-4">
      <h3 className="label-uppercase mb-3">Council Members</h3>
      {/* Model badges */}
    </div>
    
    {/* Conversations */}
    <div className="flex-1 overflow-y-auto p-4">
      <h3 className="label-uppercase mb-3">Conversations</h3>
      {/* Conversation list */}
    </div>
  </div>
</aside>
```

---

### 3. Main Content Area

**Layout:** CSS Grid
**Gap:** 24px
**Padding:** 32px

```jsx
<main className="fixed left-[280px] top-16 right-0 bottom-0 overflow-y-auto">
  <div className="p-8">
    {/* Stage cards in grid */}
    <div className="grid grid-cols-1 gap-6">
      {/* Stage 1, 2, 3 cards */}
    </div>
  </div>
</main>
```

---

### 4. Stage Cards

**Structure:** Minimal elevation, thin borders
**Hover:** Border accent glow

```jsx
<div className="card-racing group">
  <div className="flex items-center justify-between mb-4">
    <h3 className="label-uppercase">Stage 1: Initial Responses</h3>
    <span className="text-xs text-muted-foreground">4 models</span>
  </div>
  
  {/* Tab navigation - minimal style */}
  <div className="flex gap-1 mb-4 border-b border-border">
    {models.map((model) => (
      <button className="px-4 py-2 text-sm hover-racing border-b-2 border-transparent data-[state=active]:border-primary">
        {model.name}
      </button>
    ))}
  </div>
  
  {/* Content */}
  <div className="markdown-content">
    {content}
  </div>
</div>
```

---

### 5. Model Status Badges

**Style:** Minimal, uppercase, monochrome

```jsx
<div className="inline-flex items-center gap-2 px-3 py-1.5 border border-border rounded-sm text-xs font-medium uppercase tracking-wide">
  <div className="w-1.5 h-1.5 rounded-full bg-accent" />
  GPT-5.2
</div>
```

---

### 6. Input Field

**Style:** Full width, minimal chrome, sharp focus ring

```jsx
<div className="relative">
  <textarea
    className="w-full bg-card border border-border rounded-sm px-4 py-3 text-sm
               focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent
               placeholder:text-muted-foreground resize-none"
    placeholder="ASK COUNCIL..."
    rows={3}
  />
  <button className="absolute right-3 bottom-3 px-4 py-1.5 bg-primary text-primary-foreground
                     text-xs font-medium uppercase tracking-wide rounded-sm
                     hover:bg-primary/90 transition-colors duration-100">
    Send
  </button>
</div>
```

---

### 7. Command Palette (Future)

**Trigger:** Cmd/Ctrl + K
**Style:** Centered modal, glass effect optional
**Purpose:** Quick navigation, model switching

```jsx
<div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-start justify-center pt-[20vh]">
  <div className="w-full max-w-2xl bg-card border border-border rounded-sm shadow-2xl">
    <input
      type="text"
      className="w-full px-6 py-4 bg-transparent border-b border-border text-lg
                 focus:outline-none placeholder:text-muted-foreground"
      placeholder="Search commands..."
    />
    <div className="max-h-[400px] overflow-y-auto p-2">
      {/* Command items */}
    </div>
  </div>
</div>
```

---

## Motion Guidelines

### Transitions
- Duration: 100ms (fast, snappy)
- Easing: linear (no playful curves)
- Properties: colors, opacity, border

### Hover States
```css
.hover-racing {
  transition: color 100ms linear, border-color 100ms linear;
}
```

### Focus States
```css
focus:outline-none
focus:ring-2
focus:ring-ring
focus:ring-offset-0
```

---

## Layout Behavior

### Breakpoints (Desktop First)
- Large: 1280px+ (primary target)
- Medium: 1024px-1279px (scale down padding)
- Small: 768px-1023px (stack sidebar, collapsible)

### Grid System
```css
/* Prefer CSS Grid over Flexbox for structured layouts */
.main-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 0;
}
```

---

## Implementation Steps

### Phase 1: Foundation (30 min)
1. ✅ Install dependencies
2. Replace `index.css` with Tailwind + theme tokens
3. Update `tailwind.config.js` with sharp radius settings
4. Add Inter font import to `index.html`

### Phase 2: Layout Shell (45 min)
5. Create `TopNav.jsx` component
6. Create `LeftSidebar.jsx` component  
7. Create `MainContent.jsx` layout wrapper
8. Update `App.jsx` to use new layout structure

### Phase 3: Component Redesign (60 min)
9. Redesign `Sidebar.jsx` with minimal style
10. Redesign `ChatInterface.jsx` with structured cards
11. Redesign `Stage1.jsx`, `Stage2.jsx`, `Stage3.jsx` with tabs
12. Add model status badges

### Phase 4: Polish (30 min)
13. Add hover states and transitions
14. Implement focus management
15. Test keyboard navigation
16. Final spacing and typography review

---

## Utility Class Patterns

### Card Pattern
```jsx
className="bg-card border border-border rounded-sm p-6 hover:border-accent/50 transition-colors duration-100"
```

### Button Pattern (Primary)
```jsx
className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium uppercase tracking-wide rounded-sm hover:bg-primary/90 transition-colors duration-100"
```

### Button Pattern (Secondary)
```jsx
className="px-4 py-2 bg-secondary text-secondary-foreground text-sm font-medium rounded-sm hover:bg-secondary/80 transition-colors duration-100"
```

### Label Pattern
```jsx
className="text-xs font-medium tracking-wider uppercase text-muted-foreground"
```

---

## Next Actions

**For Cursor/v0:**
1. Generate TopNav component using this spec
2. Generate LeftSidebar component using this spec
3. Generate redesigned Stage cards using this spec

**Manual:**
1. Replace index.css (see tokens above)
2. Update tailwind.config.js radius to 0.125rem
3. Add Inter font to index.html

---

## Reference Links

- tweakcn.com themes: Industrial, Motorsport, Editorial
- racing.porsche.com for visual inspiration
- shadcn/ui docs for component primitives

**Color Philosophy:**
Monochrome base (graphite blacks, cool grays) + controlled blue accent
High contrast text (98% vs 6%)
No gradients, no glass, no decorative elements

**Typography Philosophy:**
Clear weight separation (medium vs normal, never bold)
Uppercase labels for structure
Large section titles (2xl+)
Compact body (sm/base)

---

## Success Metrics

✓ Feels engineered, not styled
✓ Instantly readable hierarchy
✓ Every element has purpose
✓ No visual noise
✓ Fast, snappy interactions
✓ Porsche-level restraint achieved
