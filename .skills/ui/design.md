---
name: Obsidian Protocol
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#c1c6d7'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#8b90a0'
  outline-variant: '#414755'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e69'
  primary-container: '#4b8eff'
  on-primary-container: '#00285c'
  inverse-primary: '#005bc1'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#ca8100'
  on-tertiary-container: '#3e2400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a41'
  on-primary-fixed-variant: '#004493'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-base:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.5'
  mono-code:
    fontFamily: Space Grotesk
    fontSize: 13px
    fontWeight: '500'
    lineHeight: '1.6'
    letterSpacing: -0.01em
  label-caps:
    fontFamily: Space Grotesk
    fontSize: 11px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.05em
spacing:
  unit: 4px
  gutter: 16px
  margin: 24px
  container-max: 1440px
  stack-dense: 8px
  stack-relaxed: 20px
---

## Brand & Style

The brand personality is engineered, precise, and authoritative. It targets infrastructure engineers and DevOps professionals who value speed and clarity over ornamentation. The design system utilizes a **Technical High-Contrast** style, blending elements of Minimalism with structural Brutalism. 

The aesthetic is reminiscent of a high-end IDE or a mission-control terminal. It prioritizes information density and mechanical accuracy, evoking an emotional response of total control and reliability. The visual language avoids decorative fluff, using structural lines and purposeful color theory to guide the user through complex deployment workflows.

## Colors

The palette is built on a foundation of "Deep Space" grays to minimize eye strain during long-tail debugging sessions. 

- **Primary (Electric Blue):** Reserved exclusively for primary actions and interactive states.
- **Secondary (Emerald Green):** Used for "Healthy" status, successful deployments, and active upstream nodes.
- **Tertiary (Warning Gold/Amber):** Indicates "Deploying" or "Degraded" states.
- **Semantic Red:** (#EF4444) Critical errors, failed health checks, and destructive actions.

The contrast ratio is strictly maintained at high levels to ensure legibility of dense configuration text against the dark background. Surfaces are layered using slight variations in luminosity rather than saturation.

## Typography

This design system employs a dual-font strategy. **Inter** provides a highly legible, neutral canvas for standard UI elements and body text. **Space Grotesk** is used for headlines and—crucially—as the "technical" font for labels, configuration data, and logs. While technically a sans-serif with geometric qualities, its tabular spacing and technical character make it ideal for monospaced contexts in this system.

All technical data (IP addresses, NGINX directives, status codes) must be rendered in the `mono-code` style. Labels for metrics and metadata should use `label-caps` for a distinct, dashboard-inspired look.

## Layout & Spacing

The system uses a **Fixed-Fluid Hybrid Grid**. Sidebars and telemetry panels occupy fixed widths (280px and 320px respectively), while the central orchestration area scales to fill available space. 

A strict 4px base unit ensures a dense, compact UI. Information density is prioritized; vertical rhythm is tight to allow developers to view more lines of code and more server instances without excessive scrolling. Gutters are kept thin (16px) to reinforce the "instrument cluster" feel.

## Elevation & Depth

Elevation is communicated through **Tonal Layering** and **Subtle Borders** rather than shadows. In a high-contrast dark theme, shadows often become muddy; instead, we use:

1.  **Base Layer:** The darkest value (`#020617`), used for the main application background.
2.  **Surface Layer:** A slightly lighter value (`#0F172A`) for cards, panels, and navigation.
3.  **Stroke Accentuation:** 1px solid borders (`#1E293B`) define the perimeter of all containers.
4.  **Active State:** When an element is focused or active, the border color shifts to the Primary Electric Blue, or a subtle inner glow is applied.

Depth is perceived as a "stack" of physical plates. Higher-level elements (like Modals) utilize a 1px border in a lighter gray to pop against the darker background layers.

## Shapes

The design system adopts a **Sharp (0px)** or **Near-Sharp** approach. 90-degree angles are used for all major containers, cards, and input fields to reinforce the feeling of technical precision and grid-alignment. 

Small exceptions are made for "Status Pills" or "Action Buttons" which may use a microscopic radius (2px) to prevent visual vibrating at high contrast, but for the purpose of the system tokens, the setting is `0`. This creates a modular, block-based layout that feels like an integrated development environment.

## Components

### Buttons & Inputs
- **Buttons:** Sharp corners, high-contrast fills. Primary buttons use Electric Blue. Secondary buttons are ghost-style with a subtle white border.
- **Inputs:** Darker than the surface layer with a persistent bottom-border or full 1px border. Use the monospace font for all input values.

### Status Indicators
- **Health Gauges:** Use the Emerald Green for 100% health. Use a "Pulse" animation for active deployments.
- **Badges:** Small, rectangular chips with monospaced text. Backgrounds are low-opacity versions of the status color (e.g., 10% Green fill with 100% Green text).

### Code & Config Blocks
- **The Config Editor:** Deep black background (`#000000`) with syntax highlighting optimized for NGINX directives. 
- **Logs:** A dense, terminal-style component with no padding between lines and a dedicated scrollbar that remains visible.

### Data Tables
- Row-based layout with no vertical borders, only horizontal dividers. High-density padding. Hovering a row highlights it with a 2px Electric Blue left-accent.

### Deployment Timeline
- A vertical or horizontal "stepper" component using the Tertiary Gold for "In Progress" and the Electric Blue for "Ready to Promote."