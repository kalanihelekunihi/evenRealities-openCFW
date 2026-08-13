# G2 EvenHub common-list container recovery

The six-anchor / 6,746-byte retained-path view expands to fourteen functions /
7,342 body bytes plus 1,246 owned literal/alignment bytes. The complete object
is `[0x004DCCD8,0x004DEE64)`, 8,588 physical bytes. The preceding CRC helper
belongs to `common_image_container.c`; the two helpers before the first list
anchor are list-owned style and row-offset functions. The next object begins
with pathless code at `0x004DEE64`, providing an exact physical boundary.

The audit pins 2,710 reachable instructions, 458 direct calls, 46 whole-image
BL entries, two stored animation callbacks, four path cells, and zero strict-
interior ingress. Two indirect calls share the instance selection callback.
The constructor has exactly two callers, at `0x0049506E` and `0x004959D6`,
and both load the same Thumb pointer `0x004949C1`. Its 178-byte target body has
67 reachable instructions, eleven direct calls, and no indirect calls.

Every reusable direct edge is classified: 310 EasyLogger calls at
`a596b264…`; 91 LVGL calls at selected hybrid commit `344c7c318…`; three
bounded IAR DLIB calls; six calls to the production-routed TLSF-backed heap
wrappers; and nine calls to already bounded G2 queue/event/UI providers. No
third-party implementation body or new version discriminator is embedded.

The object is not production-routed. Remaining work is first-party container
source reconstruction and display/input validation, not dependency discovery.
