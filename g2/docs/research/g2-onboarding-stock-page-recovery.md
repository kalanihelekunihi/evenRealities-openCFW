# G2 onboarding stock-page recovery

The ten-anchor / 6,624-byte retained-path view expands to 17 functions / 7,500
body bytes plus 364 interleaved literal/alignment bytes. The complete object is
`[0x0050CA24,0x0050E8DC)`, 7,864 physical bytes. All 17 functions were present
in the authenticated Ghidra inventory; the audit additionally pins 2,818
reachable instructions, two inline literal islands, 629 direct calls, 38
whole-image BL entries, both physical boundaries, and zero stored, indirect,
or strict-interior ingress.

The object constructs and lays out the onboarding stock carousel, copies stock
records into three-item pages, updates text and visibility, and coordinates
with the onboarding controller and main-page state. Its reusable graph is
fully classified: 447 calls reach 30 admitted LVGL entries at selected hybrid
commit `344c7c318…`; 110 calls reach EasyLogger at `a596b264…`; two calls are
the exact CMSIS-FreeRTOS `osMutexAcquire`/`osMutexRelease` wrappers at
`d213f261…` over FreeRTOS-Kernel `def7d2df…`; and five calls are bounded IAR
DLIB copy/fill primitives. The remaining 33 calls reach already bounded G2
onboarding, string, and common-UI providers.

No third-party implementation body is embedded, no selected dependency
interval is narrowed, and no private G2 generating commit is recoverable from
this object. It is not production-routed. Remaining work is first-party UI
source reconstruction, asset recovery, integration, and hardware/display
validation rather than unidentified utility code.
