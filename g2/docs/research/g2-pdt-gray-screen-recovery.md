# G2 production gray-screen recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed.

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
No authenticated first-party source/license is available, and OpenCFW claims
no production ownership. `tools/analyze_g2_pdt_gray_screen.py` reproduces the
complete closure from the official image.
