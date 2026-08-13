# G2 dashboard layout dependency boundary

The four retained-path anchors / 710 bytes expand to eleven functions /
2,162 body bytes for `app\gui\dashboard\dashboard_layout.c`. The complete
physical object is `[0x00558030,0x0055894C)`, 2,332 bytes. Ghidra discovered
four functions; seven source-order routines were restored, completing the
layout selection, persistence, and file-backed layout management logic.

## Extent and boundaries

The object opens at `0x00558030`, immediately after a two-byte zero pad that
closes the LVGL `lv_bar.c` cluster. Three leading helpers (`0x00558030`,
`0x00558040`, `0x00558050`) are called only from inside the anchored
dashboard-layout body (BL sites `0x005584DA`, `0x0055856E`, and the
`0x00558050` body itself), which ties them to this object rather than the
preceding LVGL widget code. The first anchored function `0x00558148` follows
the six-byte thunk `0x00558142` (`ldr.w r0,[pc,#0x764]; bx lr`), which is
called exclusively from closed dashboard objects (`ui_DashBaord_Main_Screen.c`
at `0x004E8058`/`0x004E963A`, page-state-sync at `0x004FFEB8`, and
`0x0050054C`). The object closes with a single 170-byte trailing literal pool
holding the path-pointer cell `0x005588B8`; the closed
`pb_service_quicklist.c` object begins at `0x0055894C`. Boundary slices of 16
bytes on both sides are hash-pinned.

## Function inventory and noncode

All eleven functions are fully flow-covered with no embedded data and no
inter-function gaps: the code is contiguous from `0x00558030` to
`0x005588A2`. Noncode is exactly the 170-byte trailing pool. Four functions
are path-anchored (`0x00558148`, `0x00558632`, `0x0055876A`, `0x00558804`);
the fifteen path-pointer literal references all land inside the recovered
body, proving no further path-logging code hides in the pool.

## Ingress closure

Thirty-two whole-image direct BL entry sites (twenty-one external to the
physical object) are pinned; there are no stored function entry pointers and
no strict-interior ingress. One raw BL decode at `0x006D3170` targeting
interior `0x00558590` originates in the read-only string/data region (no
Ghidra or recovered function covers the site); its 16-byte context is
hash-pinned as a data-window collision. One unaligned stored odd word at
`0x00541033` names interior `0x005580F5`; the cell is not 4-aligned, so it is
a pseudo-pointer window, not a linker-emitted callback.

## Provider boundary

All 87 external direct calls terminate at admitted providers: EasyLogger
(75), bounded IAR DLIB primitives (4: `0x00439BE4` fill/format and
`0x0044B610` `strncmp`), and the closed first-party file runtime (8:
`open_cfw_file_open`, `open_cfw_file_close`, `open_cfw_file_remove`,
`open_cfw_file_mkdir`, `open_cfw_file_opendir`, `open_cfw_file_closedir` of
`product\s200\app\config\redirect.c`). There are no LVGL, CMSIS-FreeRTOS, or
FreeRTOS kernel edges and therefore no RTOS seams in this object. The object
embeds no third-party implementation and adds no new version or private
generating-commit discriminator.

## Limitations

The seven restored functions carry source-order and call-graph evidence
only; their original C names are unobservable. The object is not
production-routed; first-party layout recreation and device display
validation remain open work.
