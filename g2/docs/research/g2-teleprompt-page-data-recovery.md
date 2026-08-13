# G2 `teleprompt_page_data.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained path is `app\gui\teleprompt\teleprompt_page_data.c`. Nine
path-anchored functions and twelve adjacent or Ghidra-missed helpers form one
closed 21-function object at `[0x0058A8E0,0x0058BCE0)`. Function bodies
contribute 4,728 bytes with SHA-256
`5da153c2173a50fe75a00f5085a162b9ceda69964b9e29aa0daeb521f8177770`;
seven alignment/literal regions contribute 392 bytes with SHA-256
`29c0ca1038ac82167e6718bcff0ea676fafe1388296d85fe4522e3e44516b3eb`.
The complete 5,120-byte physical object has SHA-256
`39167e7d97a2f9d2c125882edef4fc235ec5f3063b5f3e156476e8c783f67649`.
The preceding bytes are the prior object's literal pool and the first
`teleprompt_file_list.c` function begins at `0x0058BCE0`, closing both
boundaries.

The missed callback at `0x0058B058` is especially important: the timer-create
body materializes Thumb entry `0x0058B059` with an `ADDW` rather than a stored
pointer. Its exact diagnostic name survives even though Ghidra omitted the
function boundary. The complete byte ledger is pinned in
`tools/manifests/g2-teleprompt-page-data-function-map.tsv`.

## Cache ABI

The object owns a 20,900-byte control block at `0x2010A328`. Its first 20,880
bytes are a 20-slot ring cache:

| Slot offset | Meaning |
| ---: | --- |
| `0x000` | page identifier and page payload; 1,036 bytes copied as a unit |
| `0x40C` | state: 0 empty, 1 loading, 2 loaded |
| `0x410` | request timestamp in milliseconds |

Each slot is `0x414` bytes and page `n` maps to `n % 20`. A loaded slot is
valid only when both its state is 2 and its stored page identifier equals the
requested page. This prevents stale ring entries from aliasing a later page.
`teleprompt_page_data_get` copies the 1,036-byte page into the scratch object
at `0x2006B11C` while holding the mutex and returns that copy, rather than a
pointer into the mutable ring.

The 20-byte tail starts at `0x5190`: total pages, current window start, the
four-visible-page readiness flag, last window-change time, initialized byte,
and window-valid byte. The mutex and timer handles live at `0x20074A6C` and
`0x20074A70`.

## Window and preload behavior

The visible window is four pages. The ensure band extends five pages before
the window start and eight pages after it, clipped to `[0,total_pages-1]`, so
at most 14 pages are considered. A requested window start is clamped so a
five-page tail remains when possible. Initialization clears the entire state,
stores total-pages, and seeds the window from one page before the requested
start when that page exists.

Requests are serialized by the page-data mutex. A page already loaded is
skipped. Repeated requests within 500 ms are debounced, while a slot that has
remained in loading state for at least 5,000 ms is eligible for retry. The
preload timer runs at 2,500 ms. Its callback first prioritizes missing pages in
the four-page visible window, then searches the full ensure band. When no
requestable page exists but the band is not complete, it restarts the timer.

An update validates the page range and ring identity, copies `0x40C` bytes,
and marks the slot loaded. When all available pages in the visible four-page
window become loaded for the first time, it raises the observed loading-done
event. Deinitialization stops and deletes the timer, clears all state, releases
and deletes the mutex, and zeros both handles.

## Ingress and ownership

Across the image, 81 `BL` encodings target exact entries: 17 external and 64
within this object. The 21 bodies contain 276 direct call sites. No stored
function pointer, direct branch, or `B.W` targets an entry or strict interior.
The callback entry is constructed transiently by code and is pinned
separately. Two odd-address all-byte numeric windows resemble strict-interior
values; one overlaps Thumb instruction bytes and one lies in packed data, so
neither is a pointer or a control-flow instruction. Real strict-interior
ingress is zero.

The historical source tree and license remain unavailable. This closure is
binary evidence, not source ownership: there is no clean-room candidate, the
object is absent from `overlay.json`, and OpenCFW claims zero production bytes.
