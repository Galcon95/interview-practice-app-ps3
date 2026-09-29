---
name: Emerald Sentinel AI
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#3e4a3d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#6e7b6c'
  outline-variant: '#bdcaba'
  surface-tint: '#006e2d'
  primary: '#006b2c'
  on-primary: '#ffffff'
  primary-container: '#00873a'
  on-primary-container: '#f7fff2'
  inverse-primary: '#62df7d'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#006b2d'
  on-tertiary: '#ffffff'
  tertiary-container: '#00873b'
  on-tertiary-container: '#f7fff3'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#7ffc97'
  primary-fixed-dim: '#62df7d'
  on-primary-fixed: '#002109'
  on-primary-fixed-variant: '#005320'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#6bff8f'
  tertiary-fixed-dim: '#4ae176'
  on-tertiary-fixed: '#002109'
  on-tertiary-fixed-variant: '#005321'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
  surface-canvas: '#f8fafc'
  surface-card: '#ffffff'
  surface-card-subtle: '#f7f9f8'
  surface-tint-green: '#f0fdf4'
  border-subtle: '#e2e8f0'
  border-subtle-green: '#bbf7d0'
  hud-surface: '#0b1a11'
  hud-surface-elevated: '#1e293b'
  hud-border: '#1e3a29'
  text-primary: '#0f172a'
  text-muted: '#64748b'
  text-on-dark: '#f8fafc'
  accent-neon: '#4ade80'
  accent-emerald-dark: '#059669'
typography:
  headline-display:
    fontFamily: Plus Jakarta Sans
    fontSize: 56px
    fontWeight: '800'
    lineHeight: 64px
    letterSpacing: -0.03em
  headline-display-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '800'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.025em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
  label-badge:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.06em
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 20px
  label-kbd:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-2xs: 0.25rem
  space-xs: 0.5rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  space-3xl: 4.5rem
---

## Brand & Style

The design system establishes a high-trust, calm, and technically commanding environment engineered for high-stakes interview preparation and real-time co-pilot guidance. Its visual philosophy blends **Modern Minimalist Product UI** with high-contrast **Technical HUD / Developer Telemetry**. 

The brand personality operates on three core tenets:
- **Stealth & Composure:** Reducing cognitive load and test anxiety with crisp off-white canvas backgrounds, pristine whitespace, and quiet borders.
- **Affirmative Accuracy:** Using radiant emerald greens to denote live audio readiness, verified answers, positive performance telemetry, and instant confidence.
- **Terminal Precision:** Employing dark slate HUD components, monospaced code blocks, and audio waveform widgets to visually signal cutting-edge intelligence without cluttering the candidate's line of sight.

The target audience spans software engineers, product managers, and corporate professionals seeking discreet, ultra-fast real-time transcription, contextual cheat-sheets, and tailored interview assistance.

## Colors

The palette balances clean, high-clarity daylight surfaces with specialized dark HUD containers for tactical readouts.

- **Primary (`#16a34a`):** The definitive emerald green, driving core calls to action, active indicators, and verified states.
- **Secondary (`#0f172a`):** Deep obsidian slate, anchoring typography on light surfaces and providing the foundation for dark-mode AI HUD transcription overlays.
- **Tertiary (`#22c55e`):** Radiant neon-tinged green, reserved for live pulse rings, audio waveform visualizers, and real-time streaming tokens.
- **Neutral (`#64748b`):** Balanced slate gray, used for secondary copy, pill borders, and inactive UI controls.

### Semantic Tones & Specialized HUD Colorway
- **Light Surfaces:** Base canvas lives on `surface-canvas` (`#f8fafc`) with elevated panels on `surface-card` (`#ffffff`) and tint badges on `surface-tint-green` (`#f0fdf4`).
- **HUD Surfaces:** The live teleprompter, coding runner, and transcription inspector utilize deep emerald-tinted charcoal `hud-surface` (`#0b1a11`) framed with `hud-border` (`#1e3a29`) to preserve visual separation without eye fatigue.

## Typography

The typographic hierarchy prioritizes swift scanability and crisp legibility under time-sensitive pressure.

- **Headlines (Plus Jakarta Sans):** Geometric, contemporary, and assertive. Tight negative tracking (`-0.02em` to `-0.03em`) on large display sizes lends an authoritative, polished appearance. Highlight keywords within headlines often switch to primary emerald (`#16a34a`) for immediate focal anchoring.
- **Body & Content (Inter):** Highly legible across varied pixel densities with neutral, tall x-height geometry. Designed for effortless reading of long prompt explanations, answers, and interview suggestions.
- **HUD & Telemetry (JetBrains Mono):** Reserved for technical tokens, keyboard shortcuts (`⌘ + Enter`, `⌘ + 1`), live audio timestamps (`00:14`), syntax-highlighted code snippets, and real-time status readouts.

## Layout & Spacing

This design system uses a centered, max-width fluid container system anchored at `1200px` for marketing and documentation pages, and a flexible edge-to-edge floating layout (`1440px` max canvas) for the active co-pilot workspace.

### Grid Rhythm & Breakpoints
- **Desktop (>= 1024px):** 12-column grid, `1.5rem` (`24px`) gutters, `2rem` outer page margins. Side-by-side feature arrangements, e.g., interactive live terminal HUD paired with structured instructional copy.
- **Tablet (768px – 1023px):** 8-column grid, `1.25rem` (`20px`) gutters, `1.5rem` outer margins. Cards collapse into two-up arrangements; HUD displays fit horizontally across the central column.
- **Mobile (< 768px):** 4-column grid, `1rem` (`16px`) gutters and margins. Side-by-side modules stack vertically, with telemetry mockups scaling into full-bleed horizontal scroll containers or stacked responsive preview cards.

## Elevation & Depth

Visual hierarchy combines flat precision borders with subtle ambient diffuse drop-shadows and localized translucent dark glows.

- **Level 0 (Base Canvas):** `#f8fafc` flat background without shadow.
- **Level 1 (Standard Card / Section Box):** Pure white background `#ffffff` with a crisp `1px solid #e2e8f0` outline and a soft, spread shadow: `0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.03)`.
- **Level 2 (Interactive Hover & Modal Flyouts):** `0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04)` with border transitioning to `#cbd5e1`.
- **HUD Dark Terminal Elevation:** Deep charcoal `#0b1a11` or `#0f172a` wrapped in `1px solid #1e3a29` or `1px solid #334155`. Floating controls and pulse badges on dark canvases use soft green neon aura drops: `0 0 20px -3px rgba(34, 197, 94, 0.25)`.
- **Overlay Glass:** Top navigation bars and floating answer HUDs use `backdrop-filter: blur(12px)` over `rgba(255, 255, 255, 0.85)` (light) or `rgba(11, 26, 17, 0.85)` (HUD panel).

## Shapes

The design system standardizes on **Rounded (Level 2)** geometry:
- Standard interactive elements, input text boxes, and small telemetry boxes use `0.5rem` (`8px`) radii.
- Feature cards, simulated terminal windows, and dashboard summary modules utilize `rounded-lg` (`1rem` / `16px`) to `rounded-xl` (`1.5rem` / `24px`).
- Badges, category indicator pills, keyboard shortcut hints, and primary pill-action buttons adopt fully rounded pill profiles (`9999px` / `round-full`).
- Window controls (such as the simulated browser/app dot triggers) use perfect circular geometry (`size-3`, `rounded-full`).

## Components

### Buttons
- **Primary Action Button:** Solid `#16a34a` emerald background, text `#ffffff`, font `Plus Jakarta Sans` semi-bold (`600`). Padding: `0.75rem 1.5rem` (`rounded-full` or `rounded-lg`). Hover: `#15803d` with slight subtle scale `scale-[1.01]`. Often paired with trailing arrow icon `→`.
- **Secondary / HUD Button:** Dark `#1e293b` with `1px solid #334155`, text `#f8fafc`. Hover: `#334155`. Monospaced hotkey indicator inset on right (`⌘ + Enter`).
- **Ghost / Tertiary Button:** Transparent fill, text `#0f172a`, hover background `#f1f5f9`.

### Badges & Pill Chips
- **Category Pills:** High-contrast, soft-tinted backgrounds: `background: #f0fdf4`, `color: #15803d`, `border: 1px solid #bbf7d0`. Rendered in uppercase `label-badge` with tracking (`letterSpacing: 0.06em`).
- **Shortcut & Telemetry Badges:** JetBrains Mono pill or rounded tag with subtle border (`#334155`), dark background (`#0f172a`), highlighting quick key bindings.

### Cards & Telemetry Containers
- **Light Feature Cards:** Flat `#ffffff` surface, `1px solid #e2e8f0` border, `1.5rem` internal padding, `rounded-xl`. Feature titles include green check icons (`#16a34a`) and numerical sequential step markers (`01`, `02`, `03` in `#16a34a`).
- **Dark HUD Terminal Card:** `#0b1a11` base with `1px solid #1e3a29`. Features live audio waveform displays, avatar initial circles with active green pulse halos, and simulated real-time streaming answer dialogs.
- **Pricing Cards:** Comparison columns with the featured/recommended tier distinguished by a full green primary gradient header or solid emerald panel (`#16a34a`), white typography, and white high-contrast CTA buttons.

### Form Inputs & Checkboxes
- **Input Fields:** `#ffffff` background with `1px solid #cbd5e1`, `0.5rem` rounded corners. Focus state produces an emerald ring: `outline: none; box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2); border-color: #16a34a`.
- **Checkboxes & Radios:** Emerald active fill (`#16a34a`) with white check icon checkmark. Inactive state: `1px solid #cbd5e1`.

### Accordions & FAQs
- Sleek minimal expansion rows: pure white surface with `1px solid #e2e8f0`, rounded-lg (`0.75rem`), smooth chevron rotation, and comfortable `1.25rem` padding.