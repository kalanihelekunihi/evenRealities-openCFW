# G2 EvenHub common-text container recovery

The nine-anchor / 4,648-byte retained-path view expands to thirteen functions /
6,966 body bytes plus 774 owned literal/alignment bytes. The complete object is
`[0x004DEE64,0x004E0CA0)`, 7,740 physical bytes. Three functions missed by
Ghidra are recovered: a style wrapper, the 2,136-byte constructor, and a
94-byte text-index helper. The constructor and index helper also restore two
source-path anchors, bringing the authenticated total to eleven. The boundary
begins exactly where `common_list_container.c` ends; the next pathless helper
at `0x004E0CA0` belongs to `evenhub_main.c`.

The audit pins 2,509 reachable instructions, 445 direct calls, 24 whole-image
BL entries, three stored animation callbacks, three path cells, and zero
strict-interior ingress. Four indirect calls share the instance navigation
callback. The constructor has exactly two callers, at `0x00495252` and
`0x00495BBE`, and both load Thumb pointer `0x00494A79`. Its `evenhub_ui.c`
target at `[0x00494A78,0x00494B38)` is 192 bytes, with 73 reachable
instructions, eleven direct calls, and no indirect calls.

Every reusable direct edge is classified: 325 EasyLogger calls at
`a596b264…`; 78 LVGL calls at selected hybrid commit `344c7c318…`; five
bounded IAR DLIB calls; six calls to the production-routed TLSF-backed heap
wrappers; and twelve calls to already bounded G2 text/queue/UI providers. No
third-party implementation body or new version discriminator is embedded.

The object is not production-routed. Remaining work is first-party container
source reconstruction and display/input validation, not dependency discovery.
