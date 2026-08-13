# G2 EvenHub UI recovery

The nine-anchor / 3,682-byte retained-path view expands to 26 functions /
14,296 body bytes plus 1,272 owned literal/alignment bytes. The complete object
is `[0x004935CC,0x0049729C)`, 15,568 physical bytes. Ghidra discovered ten
functions; sixteen additional functions recover the missing lifecycle,
container, parsing, callback, and side-specific page implementations. Seven
retained-path literal cells authenticate 21 of the complete functions. The
object starts after `evenhub_loading_Page.c` data and ends immediately before
the pathless `service_ancc.c` helper cluster.

The audit pins 5,159 reachable instructions, 855 direct calls, 44 whole-image
BL entries, ten stored callback pointers, and zero strict-interior ingress.
Both indirect sites are exact. The two callers of the iterator at `0x00493EE6`
load `0x004940E9`; the four callers of the injector constructor at
`0x004942A4` load the side-specific callbacks `0x00495F9B` or `0x004961E5`.
All three target bodies are already inside the authenticated object.

Every reusable direct edge is classified: 690 EasyLogger calls at
`a596b264…`; 37 LVGL calls at selected hybrid commit `344c7c318…`; seven
nanopb calls at selected compatibility commit `98bf4db6…`; 22 bounded IAR
DLIB calls; ten calls to production-routed TLSF-backed heap wrappers; two calls
to closed LZ4 adapters; and 55 calls to bounded first-party role, transport,
container, and EvenHub providers. No third-party implementation body or new
version discriminator is embedded.

The object is not production-routed. Remaining work is first-party EvenHub UI
source reconstruction and display/input validation, not dependency discovery.
