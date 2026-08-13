# G2 onboarding news-page recovery

The nineteen-anchor / 7,006-byte retained-path view expands to 35 functions /
9,346 body bytes plus 1,294 interleaved and post-text literal/alignment bytes.
The complete object is `[0x0050A094,0x0050CA24)`, 10,640 physical bytes, ending
exactly where the closed stock-page object begins. The audit pins all 3,494
reachable instructions, 544 direct calls, 85 whole-image BL entries, one
stored callback pointer, all five path cells, and both physical boundaries.

A raw halfword scan finds apparent calls from `0x0048A484` to `0x0050A5A2`
and from `0x0048A4A4` to `0x0050A5C2`. They are not ingress: each starts at
the second halfword of a reachable four-byte `uxtab` instruction at
`0x0048A482` or `0x0048A4A2`. The analyzer independently decodes the enclosing
function and fails closed unless both overlap proofs remain exact. Qualified
strict-interior ingress and indirect calls are therefore both zero.

Every reusable edge is classified: 232 LVGL calls at selected hybrid commit
`344c7c318…`; 160 EasyLogger calls at `a596b264…`; sixteen exact
CMSIS-FreeRTOS mutex-wrapper calls at `d213f261…` over FreeRTOS-Kernel
`def7d2df…`; fifteen bounded IAR DLIB calls; one call to the production-routed
ARM EABI unsigned division reconstruction; and two calls to the closed G2 time
service. The remaining 44 calls reach already bounded onboarding, main-page,
string, and common-UI providers.

No third-party implementation body is embedded, no dependency interval is
narrowed, and no private G2 generating commit is recoverable. The object is
not production-routed. Remaining work is first-party news/UI reconstruction,
assets, integration, and hardware/display validation rather than unidentified
utility code.
