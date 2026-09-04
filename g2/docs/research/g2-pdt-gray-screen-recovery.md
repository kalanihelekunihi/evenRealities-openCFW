# G2 production gray-screen recovery

Status: complete linked-object census, clean-room production C implementation,
dual-profile source routing, and fail-closed behavioral verification. Physical
panel validation is blocked by unavailable authorized G2 hardware evidence.

The retained `app\gui\PdtGrayScreen\pdt_gray_screen.c` object occupies
`[0x005CF634,0x005CF7A8)`: three bodies / 340 bytes and a 32-byte pool, for
372 physical bytes. The body and physical SHA-256 values are respectively
`123af7b5377985763178d0cc2208acfe93e627bf24280ee59335297d0ba92fff`
and `cc54723cf804434f6c43210a0f6cfa27ac08f770a199cd199f69d157598f6db8`.

The bodies are the exact retained `PdtGrayScreen_common_data_handler`
(`[0x005CF634,0x005CF67A)`), a four-byte always-true predicate, and the
266-byte screen event handler. All three entries are pointer-routed. Descriptor
`0x006A45D0` binds screen ID `0x10F`, the data/UI handlers, and state
`0x20003080`; pointer cell `0x0079373C` binds the predicate. There are no BL or
`B.W` entries, strict-interior targets, or other stored body/interior values.
The 23 body calls and all retained literals are pinned.

On event 2 the handler creates a 640 by 480 root and eight 72 by 288 vertical
bands. Stock factors `[1,2,4,8,8,4,2,1]` are multiplied by 17 to form symmetric
gray values `[17,34,68,136,136,68,34,17]`. It publishes the root at
`0x20074880` and `0x20003084`. Event 3 is a recognized no-op; other events also
return without construction. The data handler only logs the received length
and returns zero, while the predicate always returns one.

The following `ProductionTest` handler begins at `0x005CF7A8`; its matching
path and descriptor at `0x006A45E0` independently close the object boundary.
OpenCFW now owns a clean-room MIT implementation in
`components/apollo_main/core_overlay/pdt_gray_screen.c`, with its ABI in
`pdt_gray_screen.h`. All three stock entries are source-routed for reviewed
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 builds. The compiled callbacks
occupy 250 bytes plus two alignment bytes in each profile, and the event leaf
has an exact 18-call relocation contract to retained LVGL providers. All 340
stock body bytes are displaced; the 32-byte diagnostic/literal pool remains
retained.

`tools/analyze_g2_pdt_gray_screen.py` now pins the source and header, three
production leaves, provider targets, stock entry redirects and NOP fill,
dual-profile compiled text, manifest ownership, package consistency, and the
original object evidence. The host runtime test verifies the registered ABI,
root publication, object count, flags, geometry, scrollbar mode, gray values,
and no-op events. No hardware write or flash operation was performed. Closing
physical validation requires an authorized G2 panel trace confirming the black
640×480 root and eight 72×288 bands at x positions 0 through 504 in 72-pixel
steps, with gray values 17, 34, 68, 136, 136, 68, 34, and 17.
