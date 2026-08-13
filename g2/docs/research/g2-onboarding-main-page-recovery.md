# G2 onboarding main-page recovery

The seven-anchor / 3,648-byte census view expands to 52 functions / 9,234 body
bytes plus 542 interleaved pool/alignment bytes. The complete object occupies
`[0x004A8560,0x004AAB90)`, 9,776 physical bytes. Fifteen source-order and
stored-callback bodies were absent from the authenticated Ghidra function list.
The audit pins all 3,632 instructions, 533 direct calls, 118 BL entries, 17
stored pointers, both boundaries, and zero indirect or strict-interior ingress.

Every reusable edge is classified: 264 LVGL calls at selected hybrid commit
`344c7c318…`; 45 EasyLogger calls at `a596b264…`; 23 exact CMSIS-FreeRTOS
tick/mutex wrapper calls at v10.5.1 commit `d213f261…` over FreeRTOS-Kernel
`def7d2df…`; 17 bounded IAR DLIB memory/string/format calls; four calls to the
admitted mpaland formatter at `d3b98468…`; and one call into the closed
nanopb-backed onboarding protobuf service. The remaining 99 calls are
first-party page, animation, display, and sibling onboarding policy.

No third-party body is embedded, no existing dependency interval is narrowed,
and no private G2 generating commit is recoverable. The object is not
production-routed; remaining work is first-party UI reconstruction, assets,
and hardware/display validation rather than unidentified utility code.
