---
name: Emerald Intelligence
colors:
  surface: '#081612'
  surface-dim: '#081612'
  surface-bright: '#2e3c37'
  surface-container-lowest: '#04110d'
  surface-container-low: '#101e1a'
  surface-container: '#14221e'
  surface-container-high: '#1f2d28'
  surface-container-highest: '#293833'
  on-surface: '#d6e6df'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#d6e6df'
  inverse-on-surface: '#25332f'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#45dfa4'
  on-secondary: '#003825'
  secondary-container: '#00bd85'
  on-secondary-container: '#00452e'
  tertiary: '#98da27'
  on-tertiary: '#213600'
  tertiary-container: '#78b300'
  on-tertiary-container: '#283f00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#68fcbf'
  secondary-fixed-dim: '#45dfa4'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#b2f746'
  tertiary-fixed-dim: '#98da27'
  on-tertiary-fixed: '#121f00'
  on-tertiary-fixed-variant: '#334f00'
  background: '#081612'
  on-background: '#d6e6df'
  surface-variant: '#293833'
typography:
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 15px
    fontWeight: '500'
    lineHeight: 20px
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  metric-display:
    fontFamily: Space Grotesk
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.03em
  data-mono-lg:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 18px
  data-mono-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.02em
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.25rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 1.75rem
---

## Brand & Style

This design system embodies high-precision retail intelligence and algorithmic forecasting through a luminous, deep emerald aesthetic. It departs from sterile monochrome dashboards by leveraging deep forest and bioluminescent emerald hues, projecting mathematical authority, high analytical density, and effortless clarity.

The target audience includes retail supply chain directors, demand planners, inventory analysts, and merchandising executives who monitor high-volume transactional flows. The emotional response is one of calm mastery over immense data volumes: eliminating analytical fatigue through a low-strain, immersive dark canvas with glowing focus states and precise hierarchy.

The aesthetic fuses **Modern Technical Dashboard Architecture** with **Subtle Luminescence**:
- Dense, architectural card grids built on layered chromatic dark surfaces.
- Subtle inner glows and fine emerald borders (`#285544`) rather than opaque drop shadows.
- Distinct color coding for time domains: historical actuals in vibrant mint (`#34D399`) and forward-looking projections in crisp kinetic lime (`#A3E635` / `#C4F84B`).

## Colors

The palette establishes an immersive, multi-tiered dark emerald canvas where brightness indicates interaction and importance.

### Canvas & Surface Hierarchy
- **App Canvas (`#091713`):** Deepest structural base for global padding and canvas margins.
- **Sidebar Surface (`#071E18`):** Anchored, quiet background for permanent navigation modules.
- **Main Surface (`#0D241B`):** Base canvas layer for the analytical workspace.
- **Card Background (`#102D22`):** Primary container for metric panels, charts, and data tables.
- **Elevated / Popover (`#15392C`):** Modals, dropdown flyouts, and floating tooltips.
- **Input Fill (`#112D24`):** Embedded form fields and search containers.
- **Hover Surface (`#194735`):** Interactive state for clickable list items and tab rows.
- **Active Navigation (`#116B4A`):** Dedicated active indicator backdrop for primary routes.

### Accents & Semantic Signaling
- **Primary Accent (`#10B981`):** Action buttons, selected tags, primary KPI trends.
- **Secondary Accent (`#34D399`):** Historical trendlines, active chart dots, secondary metrics.
- **Forecast Accent (`#A3E635` / `#C4F84B`):** Exclusively reserved for predictive curves, forecast regions, and AI recommendations.
- **Critical / Negative (`#F87171`):** Downward shifts, anomalies, or stockout alerts.

### Text Hierarchy
- **Text Primary (`#E9FFF5`):** High-readability tinted white for titles, values, and active labels.
- **Text Secondary (`#B7D6C8`):** Body copy, structural labels, and axis markers.
- **Text Muted (`#8FAE9F`):** Unit descriptions, disabled states, and metadata timestamps.

### Outlines & Borders
- **Standard Border (`#285544`):** Card enclosures and table row dividers (1px solid).
- **Highlight Border (`#3D795C`):** Active container outline, input focus rings, and glowing card edges.

## Typography

The typography leverages three distinct typefaces to enforce cognitive separation between brand/architecture, narrative explanation, and numerical precision:

1. **Space Grotesk (Brand & Headers):** Applied to view titles, module headers, and large metric cards. Its technical geometry pairs naturally with algorithmic intelligence.
2. **Inter (UI Chrome & Content):** Delivers clean readability across dense control bars, table narrative columns, tooltips, and system notifications.
3. **JetBrains Mono (Data, Codes, & Telemetry):** Used for stock keeping units (SKUs), tabular metrics, percentage deltas, axis labels, and model accuracy statistics (`MAE`, `RMSE`). Numerical columns must use `font-variant-numeric: tabular-nums` to eliminate jitter across data updates.

## Layout & Spacing

The system implements a structured 12-column grid balanced for maximum viewport utilization without visual clutter.

### Layout Model
- **Fixed Sidebar:** A 240px wide sidebar anchored left (`#071E18`), maintaining persistent navigation hierarchy.
- **Fluid Workspace:** Content scales smoothly between 1024px and 1920px. On wide screens (>1600px), dashboards maintain fixed 1.25rem gutters to avoid data sprawl.
- **Multi-Panel Structure:** Dashboard templates utilize a split 8:4 column layout: 8 columns dedicated to core time-series visualizers and primary KPIs; 4 columns dedicated to product drilldown selectors, forecast breakdowns, and automated recommendation engines.

### Responsive Breakpoints
- **Desktop (>= 1280px):** 12 columns, 1.25rem gutters, persistent left sidebar.
- **Tablet (768px - 1279px):** 8 columns, 1rem gutters, collapsible icon-only rail (64px). Secondary panels stack below the primary chart module.
- **Mobile (< 768px):** 4 columns, single-column stacked cards, bottom navigation drawer replacing the persistent sidebar.

## Elevation & Depth

Visual depth is achieved through layered tonal luminance and subtle emerald edge illumination rather than heavy black drop shadows.

### Elevation Hierarchy
- **Level 0 (Canvas Base - `#091713`):** The structural bed. No borders, pure absorbing background.
- **Level 1 (Card & Module - `#102D22`):** Standard data cards. Bounded by a 1px border (`#285544`). Inner diffuse glow applied via `box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04)`.
- **Level 2 (Hover & Active States - `#194735`):** Interactive cards and row hovers. Border elevates to `#3D795C` with an ambient glow of `0 0 16px -4px rgba(16, 185, 129, 0.15)`.
- **Level 3 (Overlays & Flyouts - `#15392C`):** Modals, search dropdowns, and date pickers. Border of 1px solid `#3D795C`, paired with a deep shadow of `0 12px 32px -8px rgba(0, 0, 0, 0.6)`.

### Glass & Backdrop Treatments
Search bars and floating KPI badges apply subtle hardware-accelerated backdrop blur (`backdrop-filter: blur(12px)`) with 85% opacity on surface fills to allow background trends to register subtly beneath floating interfaces.

## Shapes

The interface balances sharp analytical rigor with polished ergonomics using balanced curvature (`roundedness: 2`):

- **Small Controls (Buttons, Inputs, Badges):** 0.5rem (8px) radius for tight, structured alignment.
- **Cards & Data Modules:** 0.75rem - 1rem (12px - 16px) radius for clean, modern containment.
- **Pill Elements (Time Switchers, Status Tags, Trend Badges):** Full pill (9999px) radius to distinguish state switches and quick filters from square metric cards.

## Components

### Buttons & Interactive Controls
- **Primary Action:** Solid Emerald `#10B981` background, `#071E18` bold typography. Hover shifts to `#34D399` with `box-shadow: 0 0 12px rgba(16, 185, 129, 0.35)`.
- **Secondary / Ghost:** Transparent background, `#285544` border, `#E9FFF5` text. Hover shifts to `#194735` fill and `#3D795C` border.
- **Segmented Range Controls (4W / 12W / 26W / 1Y):** Contained in a `#0D241B` track. Active pill renders in `#10B981` with `#071E18` bold text; inactive pills render in `#B7D6C8` on transparent background.

### KPI Metric Cards
- Container built with `#102D22` background, 12px padding, 12px radius, `#285544` outline.
- Top row aligns an icon badge (emerald-tinted circle/square `#11382A`) with the metric title in `#B7D6C8`.
- Metric numbers use `Space Grotesk` at 28px in `#E9FFF5`, flanked by a pill badge indicating delta direction: positive deltas in `#10B981` tint with an arrow up (`+12.4%`), negative deltas in soft coral.

### Inputs & Global Search
- Background: `#112D24`. Border: 1px `#285544`. Radius: 10px.
- Placeholder text in `#8FAE9F`. Focus state elevates border to `#3D795C` with a 2px outer ring at 20% opacity (`rgba(16, 185, 129, 0.2)`).
- Search shortcuts render inline JetBrains Mono keycap badges (e.g. `⌘K`) with `#071E18` fill and `#285544` border.

### Forecasting Visualizer (Time-Series Chart)
- **Grid Lines:** Subtle dotted `#1D4133`.
- **Historical Curve:** Solid 2.5px stroke `#34D399` with filled nodes and a vertical gradient fill tapering into `#0D241B` at 0% opacity.
- **Forecast Curve:** Dashed 2.5px stroke `#C4F84B` / `#A3E635` across the shaded forecast window (`rgba(163, 230, 53, 0.04)` background fill).
- **Data Points / Tooltips:** High-contrast tooltip anchored on hover using `#15392C` surface and `#3D795C` outline.

### Recommendation Callouts
- Highlighted cards with `#15392C` fill, an accent border in `#3D795C`, and a glowing accent icon.
- Recommendation body text uses `#A3E635` for primary proposed actions and metrics, set against `#B7D6C8` explanatory copy.