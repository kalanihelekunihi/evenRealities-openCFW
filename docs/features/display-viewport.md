# G2 Display vs Viewport Architecture

## Overview

The Even G2 smart glasses have a **two-layer display offset system** that positions a smaller visible viewport within a larger GPU framebuffer. Understanding this architecture is essential for display positioning, content alignment, and optical calibration.

## Display Stack

```
┌─────────────────────────────────────────┐
│         NemaGFX GPU Framebuffer         │
│              640 × 480 px               │
│                                         │
│   ┌───────────────────────────────┐     │
│   │    JBD4010 Visible Viewport   │     │
│   │         576 × 288 px          │     │
│   │                               │     │
│   │   (Content rendered by LVGL)  │     │
│   │                               │     │
│   └───────────────────────────────┘     │
│                                         │
│         ← up to 64px horiz →            │
│         ← up to 192px vert →            │
└─────────────────────────────────────────┘
```

### Layer 1: GPU Framebuffer (640×480)

The Ambiq Apollo510b SoC renders all display content via the NemaGFX GPU into a **640×480 pixel framebuffer**. This is the internal render target used by LVGL v9.3 for all layout, text rendering, and compositing operations.

**Source:** `displaydrv_manager.c`
```c
#define DISPLAY_FB_WIDTH   0x280  /* 640 pixels (framebuffer stride) */
#define DISPLAY_FB_HEIGHT  0x1E0  /* 480 pixels (framebuffer height) */
```

### Layer 2: Visible Viewport (576×288)

The JBD4010 micro-LED panel has a native resolution of **576×288 pixels** in **4-bit grayscale** (Gray4, 16 levels). This is the actual visible area shown to the user's eye. Content is monoscopic — both eyes display the same image.

**Source:** `displaydrv_manager.c`
```c
#define DISPLAY_WIDTH   0x240  /* 576 pixels */
#define DISPLAY_HEIGHT  0x120  /* 288 pixels */
```

## Offset System

### Compositing Offset (Viewport Position in Framebuffer)

The visible 576×288 viewport can be positioned anywhere within the 640×480 framebuffer using compositing offsets:

| Axis | Max Offset | Calculation |
|------|-----------|-------------|
| Horizontal | 64 px | 640 - 576 = 64 |
| Vertical | 192 px | 480 - 288 = 192 |

The compositing callback in `displaydrv_manager.c` computes the final offset from two additive sources:

```c
horiz_offset = buffer_sync_to_ctx_f48 + buffer_sync_to_ctx_f44;
vert_offset  = buffer_sync_to_ctx_f4c + buffer_sync_to_ctx_f40;
```

These are clamped to `MAX_HORIZ_OFFSET` (64) and `MAX_VERT_OFFSET` (192), then passed to:

```c
buffer_sync_to_fb(src, dest,
    DISPLAY_FB_WIDTH, DISPLAY_FB_HEIGHT,  /* 640, 480 */
    DISPLAY_WIDTH, DISPLAY_HEIGHT,         /* 576, 288 */
    horiz_offset, vert_offset);
```

The production test firmware sets these via:
- `pt_protocol_procsr_468118(horiz)` → sets horizontal offset + triggers framebuffer refresh
- `pt_protocol_procsr_46813e(vert)` → sets vertical offset + triggers framebuffer refresh
- `pt_display_set_region(h, v)` → sets region offsets (horiz < 49, vert < 65)

### Hardware Display Offset (JBD4010 Register-Level)

A second, finer-grained offset is applied at the JBD4010 micro-LED panel register level:

```c
/* JBD4010 panel */
am_devices_jbd4010_set_display_offset(x_offset, y_offset);
// Sends SPI command 0xC0 with [x_offset, y_offset]

/* A6N-G panel (alternate source) */
am_devices_hongshi_set_display_offset(x_offset, y_offset);
// Writes registers 0xEF (x) and 0xF0 (y)
```

**Range:** x_offset: 2–22 (0x16), y_offset: 2–18 (0x12)

**Per-eye adjustment:** The right eye automatically gets `+5` added to its x_offset by firmware:
```c
if ((*g_jbd4010_is_right_eye_flag != '\0') &&
    (ble_connection_state_check() == 2)) {
    x_offset = x_offset + 5;
}
```

**Persistence:** Hardware offsets are stored in NVDB flash (keys 3 and 4) and loaded from calibration data at display init:
```c
am_devices_jbd4010_set_display_offset(
    *(uint8_t *)(g_jbd4010_display_calibration_data + 0x2c),  /* x */
    *(uint8_t *)(g_jbd4010_display_calibration_data + 0x2d)   /* y */
);
```

## Content Positioning (EvenHub Layer)

Since the compositing and hardware offsets are not directly adjustable via standard BLE services (they are factory-calibrated or set via production test protocol), the iOS app adjusts display positioning at the **content level** by applying X/Y deltas to EvenHub container coordinates.

### How Content Offset Works

1. User sets a per-eye offset in the Display Position settings
2. When EvenHub containers are created, the offset is added to all container X/Y positions
3. The content shifts within the 576×288 canvas
4. A test pattern can be sent to verify alignment

```
576×288 Canvas
┌──────────────────────────────────────┐
│                                      │
│    ┌──────────────────────┐          │
│    │  Content with offset │          │
│    │  (x+dx, y+dy)       │          │
│    └──────────────────────┘          │
│                                      │
└──────────────────────────────────────┘
```

### Offset Ranges (Content Level)

| Direction | Range | Notes |
|-----------|-------|-------|
| Left (−X) | -64 px | Shifts content left |
| Right (+X) | +64 px | Shifts content right |
| Up (−Y) | -48 px | Shifts content up |
| Down (+Y) | +48 px | Shifts content down |

These limits are conservative to prevent content from being pushed off the visible display area.

## Coordinate System

- **Origin:** (0, 0) at top-left corner
- **X-axis:** Increases rightward (0 → 576)
- **Y-axis:** Increases downward (0 → 288)
- **Color depth:** 4-bit grayscale (16 levels, 0x0=black, 0xF=white)

## Head-Up Calibration

During onboarding, the glasses run a head-up display calibration flow (state 5 = `HEAD_UP`) that adjusts the display offset based on the user's head position. The onboarding data manager sends calibration parameters via the inter-eye peer protocol:

```c
#define CMD_HEADUP_PARAMS  0x09
// Packet: [0x09, angle, calibration_status]
```

The `nav_ui_get_display_offset()` function currently returns `(0, 0)`, indicating the base offset is always zero — any non-zero offset comes from the factory calibration data stored in NVDB.

## Summary Table

| Layer | Resolution | Adjustable via BLE? | Persistence |
|-------|-----------|-------------------|-------------|
| GPU Framebuffer | 640×480 | No (production test only) | RAM (volatile) |
| Visible Viewport | 576×288 | No (factory calibration) | NVDB flash |
| Content Offset | Within 576×288 | Yes (EvenHub containers) | UserDefaults |
| Hardware Offset | x:2–22, y:2–18 | No (factory calibration) | NVDB flash |
