# EvenHub Display System

EvenHub provides custom display layouts on the G2 glasses using a container-based system. The display canvas is 576 × 288 pixels with 4-bit greyscale (16 levels, rendered as green on the micro-LED).

**Service**: `0xE0-20` (TX), `0xE0-00` (RX). Firmware handler: `evenhub_common_data_handler`.

EvenHub has its own LVGL-based container layout engine — it does NOT need DisplayConfig (0x0E-20). Only DisplayWake (0x04-20) is required before sending EvenHub commands. DisplayConfig is a separate service used by Teleprompter, Conversate, and Navigation.

**Dashboard widgets** use a separate service: `0x07-20` (shared with EvenAI), differentiated by the protobuf command type field. Dashboard data packages route through types 11-19 on the same service endpoint.

**Source**: `G2EvenHubProtocol.swift`, `G2EvenHubSender.swift`

## Operations

### CreateStartUpPageContainer

Creates a new display page with containers. This is the initial page setup.

```
Protobuf:
  field 1 (varint): containerTotalNum
  field 2 (LD): repeated ListContainerProperty
  field 3 (LD): repeated TextContainerProperty
  field 4 (LD): repeated ImageContainerProperty
```

### RebuildPageContainer

Replaces the current page layout. Same wire format as CreateStartUpPageContainer.

### TextContainerUpgrade

Updates the text content of an existing text container without rebuilding the page.

```
Protobuf:
  field 1 (varint): containerID
  field 2 (LD): containerName
  field 3 (varint): contentOffset
  field 4 (varint): contentLength
  field 5 (LD): content (UTF-8)
```

### ImageRawDataUpdate

Sends raw image data to an image container. Large images are automatically fragmented.

```
Protobuf:
  field 1 (varint): containerID
  field 2 (LD): containerName
  field 3 (LD): imageData (4-bit greyscale)
  field 4 (varint): mapSessionId      (fragmentation)
  field 5 (varint): mapTotalSize       (fragmentation)
  field 6 (varint): compressMode       (fragmentation)
  field 7 (varint): mapFragmentIndex   (fragmentation)
  field 8 (varint): mapFragmentPacketSize (fragmentation)
```

### ShutDownPageContainer

Removes the current display page.

```
Protobuf:
  field 1 (varint): exitMode (0=immediate, 1=delay)
```

## Container Types

### Text Container

Displays UTF-8 text with automatic word wrapping.

| Property | Range | Description |
|----------|-------|-------------|
| xPosition | 0-576 | X offset in pixels |
| yPosition | 0-288 | Y offset in pixels |
| width | 0-576 | Container width |
| height | 0-288 | Container height |
| borderWidth | 0-5 | Border thickness |
| borderColor | 0-16 | Greyscale shade (0=black, 15=white) |
| borderRadius | 0-10 | Corner rounding |
| paddingLength | 0-32 | Uniform padding |
| containerID | — | Unique ID for updates |
| containerName | max 16 chars | Identifier string |
| content | max 1000 chars (create), 2000 chars (upgrade) | UTF-8 text |
| isEventCapture | 0 or 1 | Enables scroll/touch events |

Text is left-aligned, top-aligned, in a single fixed-width font. No bold/italic/underline. Overflow text is scrollable if `isEventCapture=1`.

### List Container

Displays a scrollable list of items with firmware-managed scrolling.

| Property | Range | Description |
|----------|-------|-------------|
| xPosition, yPosition, width, height | same as text | Position/size |
| borderWidth | 0-5 | Border thickness |
| borderColor | 0-15 | Greyscale shade |
| borderRadius | 0-10 | Corner rounding |
| paddingLength | 0-32 | Uniform padding |
| itemCount | 1-20 | Number of list items |
| itemNames | max 64 chars each | Item label strings |
| isEventCapture | 0 or 1 | Enables selection events |

### Image Container

Displays a raster image in 4-bit greyscale.

| Property | Range | Description |
|----------|-------|-------------|
| xPosition, yPosition | 0-576/288 | Position |
| width | 20-200 | Container width |
| height | 20-100 | Container height |
| containerID | — | Unique ID for updates |
| containerName | max 16 chars | Identifier string |

Images are sent separately via ImageRawDataUpdate after the page is created.

## Constraints

| Constraint | Value |
|------------|-------|
| Max containers per page | 4 |
| Max list items | 20 |
| Max container name | 16 characters |
| Max text (create) | 1000 characters |
| Max text (upgrade) | 2000 characters |
| Image width range | 20-200 px |
| Image height range | 20-100 px |
| Display channel MTU | 204 bytes |
| isEventCapture per page | Exactly 1 container |

## Image Fragmentation

Images larger than the BLE display channel limit (204 bytes minus protobuf overhead) are automatically split into fragments:

- Each fragment shares a random `mapSessionId`
- `mapTotalSize` = total image bytes
- `mapFragmentIndex` = 0-based fragment number
- `mapFragmentPacketSize` = bytes in this fragment
- `compressMode` = 0 (uncompressed)
- Fragments must be sent sequentially (not concurrently)

## Result Codes

After container operations, the glasses respond with a result on service 0x0E-00:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid container |
| 2 | Oversize response container |
| 3 | Out of memory |

## Container Events

When a container with `isEventCapture=1` is active, the glasses send events back:

- **List click**: User selected a list item (includes item index)
- **Text click**: User tapped a text container
- **Scroll**: User scrolled content (includes direction)

## Unicode Support

The G2 display supports a subset of Unicode:

| Range | Coverage |
|-------|----------|
| ASCII & Latin (U+0020–U+00FF) | Nearly complete |
| Arrows (U+2190–U+2199) | Supported |
| Box Drawing (U+2500–U+2573) | Most characters |
| Block Elements (U+2580–U+2595) | Many characters |
| Geometric Shapes (U+25A0–U+25EF) | Selective |
| Misc Symbols (U+2605–U+261E) | 7 characters |

Not supported: Emoji, dingbats, weather symbols, most double-line box drawing.
