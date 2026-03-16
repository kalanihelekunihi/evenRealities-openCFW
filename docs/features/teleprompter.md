# Teleprompter Protocol (Service 0x06-20)

## Overview

The teleprompter service displays scrollable text on the G2 glasses. It supports:
- Manual scroll mode (swipe to scroll)
- AI auto-scroll mode (voice-triggered)
- Multiple scripts stored on device

## Message Sequence

```
1. Auth Packets (7 packets)           - Establish session
2. Display Config (0x0E-20, type=2)   - Configure display
3. Teleprompter Init (0x06-20, type=1) - Select script, set mode
4. Content Pages 0-9 (0x06-20, type=3) - First batch
5. Mid-Stream Marker (0x06-20, type=255) - Required marker
6. Content Pages 10-11 (0x06-20, type=3) - Second batch
7. Sync Trigger (0x80-00, type=14)    - Trigger rendering
8. Content Pages 12+ (0x06-20, type=3) - Final pages
```


## Message Types

### Type 1: Init/Select Script

Selects a script and configures display mode.

```
08-01           Type = 1 (init)
10-XX           msg_id (varint)
1A-XX           Field 3, length (settings block)
  08-XX         Script index (0 or 1)
  12-XX         Display settings sub-block
    08-01       Sub-field 1 = 1
    10-00       Sub-field 2 = 0
    18-00       Sub-field 3 = 0
    20-8B-02    Sub-field 4 = 267 (display width?)
    28-XX-XX    Sub-field 5 = content height (varint)
    30-E6-01    Sub-field 6 = 230 (line height)
    38-XX-XX    Sub-field 7 = viewport height (varint)
    40-05       Sub-field 8 = 5 (font size?)
    48-XX       Sub-field 9 = scroll mode
```

**Scroll Mode (field 9):**
- `0x00` = Manual mode (shows "M" indicator)
- `0x01` = AI mode (shows animation)

### Type 2: Script List

Lists available scripts on the device.

```
08-02           Type = 2 (list)
10-XX           msg_id
22-XX           Field 4, length (list content)
  0A-XX         Script entry
    0A-XX       Script ID (string)
    12-XX       Script title (string)
```

### Type 3: Content Page

Sends a page of text content.

```
08-03           Type = 3 (content)
10-XX           msg_id (varint)
2A-XX           Field 5, length (content block)
  08-XX         Page number (0-indexed, varint)
  10-0A         Line count = 10
  1A-XX         Field 3, length (text)
    [TEXT]      UTF-8 text with \n separators
```

**Text Format:**
- Each page has exactly 10 lines
- Lines separated by `\n` (0x0A)
- Text starts with `\n` (leading newline)
- Text ends with ` \n` (space + newline)
- Lines wrap at ~25 characters

### Type 4: Content Complete

Signals end of content transmission.

```
08-04           Type = 4 (complete)
10-XX           msg_id
32-XX           Field 6, length (completion info)
  08-00         Start page (0)
  10-XX         Total pages (varint)
  18-XX         Total lines (varint)
```

### Type 255 (0xFF): Mid-Stream Marker

Required marker sent during content streaming.

```
08-FF-01        Type = 255 (varint encoding)
10-XX           msg_id
6A-04           Field 13, length 4
  08-00         Sub-field 1 = 0
  10-06         Sub-field 2 = 6
```

## Example: Display Custom Text

```python
# 1. Connect and auth (7 packets)
send_auth_sequence()

# 2. Display config
send_display_config(seq=8, msg_id=20)

# 3. Init teleprompter (manual mode)
send_teleprompter_init(seq=9, msg_id=21, script_index=1, mode=0)

# 4. Send content pages 0-9
for page in range(10):
    send_content_page(seq=10+page, msg_id=22+page, page_num=page, text=pages[page])

# 5. Mid-stream marker
send_type_255(seq=20, msg_id=32)

# 6. Send pages 10-11
for page in range(10, 12):
    send_content_page(seq=21+(page-10), msg_id=33+(page-10), page_num=page, text=pages[page])

# 7. Sync trigger
send_sync(seq=23, msg_id=35)

# 8. Send remaining pages
for page in range(12, len(pages)):
    send_content_page(...)
```

## Text Formatting

The glasses display approximately:
- **25 characters** per line
- **10 lines** per page
- **~7 lines** visible at once

For best results:
- Wrap text at word boundaries
- Use explicit `\n` for line breaks
- Pad short content to minimum 14 pages

## Scroll Bar Sizing

The scroll bar size is controlled by init packet fields:
- **Field 5** (0x28): Total content height
- **Field 7** (0x38): Viewport height

Ratio: `viewport / content_height` = scroll bar size percentage

For the Bee Movie script (140 lines):
- Content height: 2665
- Viewport: 1294
- Ratio: ~49% (scroll bar takes half the track)

## Response Protocol (Glasses → Phone)

The glasses send two types of responses during teleprompter rendering. Discovered via debug log 2026-02-26.

### Service 0x06-0x00 — Per-Page ACK

Sent for every content page received. Structure:

| Field | Value | Meaning |
|-------|-------|---------|
| 1 (varint) | 166 (0xA6) | Response type constant |
| 2 (varint) | varies | Echo of the sent msg_id |
| 12 (LD) | empty | Always present, always empty |

### Service 0x06-0x01 — Rendering Progress

Sent periodically to report rendering progress. Structure:

| Field | Value | Meaning |
|-------|-------|---------|
| 1 (varint) | 164 (0xA4) | Response type constant |
| 2 (varint) | varies | msg_id of last processed page |
| 10 (LD) | nested | Rendering progress |

Field 10 nested structure:
- Empty LD (0 bytes): rendering just started
- `{field1=N}`: N pages have been rendered

The terminal progress packet (pagesRendered == totalPages) repeats **3 times** at ~1.47s intervals, possibly expecting an acknowledgement.

### Content Complete Echo

The type=4 content-complete message's field 6 (tag 0x32) contains:

| Nested Field | Value | Meaning |
|-------------|-------|---------|
| 1 | 0 | Start page index |
| 2 | 14 | Total page count |
| 3 | 140 | Content height scaling denominator |

The value 140 in field 3 confirms the formula: `content_height = (lines × 2665) / 140`.

## Known Issues

1. **Minimum content**: Less than ~10 pages may not render
2. **Script index**: Must reference existing script (0 or 1)
3. **Timing**: Auth must complete before content sends
