# G2 health-page dependency boundary

Status: complete production-routed clean-room closure of
`app\gui\health\ui_health_page.c` in authenticated stock G2 firmware
2.2.6.10. Hardware qualification is explicitly blocked by unavailable
authorized physical evidence.

The object is `[0x004FB1FA,0x004FD940)`: twelve functions / 9,414 body bytes /
10,054 physical bytes. One stored callback was restored beyond Ghidra. Nineteen
direct entries, two aligned stored pointers, and one data-only pseudo-call pin
whole-image ingress; there is no indirect call.

Its 666 external calls close as 437 selected LVGL calls, 55 admitted
EasyLogger diagnostics, four bounded IAR calls, 36 selected mpaland formatter
calls, and 134 first-party health/dashboard/navigation/service calls. There is
no direct CMSIS-FreeRTOS call, embedded reusable body, or new version or
historical producing-commit discriminator. Health layout and product policy
are implemented in `components/apollo_main/core_overlay/ui_health_page.c`.

The twelve selector-isolated Cortex-M55 leaves emit 3,978 text bytes and 328
authenticated read-only string bytes with ten alignment bytes and 269 strict
relocations. Twelve guarded redirects replace all 9,414 authenticated stock
body bytes; 640 bytes of inter-function/tail compatibility data remain
official. Host tests cover translated metrics, goal scaling, two-page
navigation, callback animation, FIFO ordering, refresh, input forwarding,
minimize, and teardown.

Canonical artifacts are:

- overlay: 330,776 bytes,
  `7363638cd535d03e9a5915f501fc1f726c7ba19c428032bda03594423c84dc2d`;
- component: 3,854,172 bytes,
  `2feb75356faca554c89d19ab25069cd15427fa2f191b3c43876aed70707c961b`;
- package: 4,632,666 bytes,
  `427187931275f6eaa93bebc65f910fcabe71c0d6f8027be3811b43c7efd2eda8`;
- flash plan: 3,067,205 bytes,
  `2066696d4597dae11c56585c59233b4b5e90ba3c69539577a1e95f28383bc9bf`,
  with 4,421 placed, two unresolved, five container-only, and six protected
  regions.

No image was signed or flashed. Live bilateral display, touch/action,
animation timing, translated-resource, and peer-page synchronization evidence
cannot be obtained: the authorized right temple is nonresponsive, the
authorized left temple must remain stock, and no responsive authorized pair or
golden health-page UI trace is available. This is a hardware-evidence blocker,
not an unimplemented software gap. Wider firmware functional completeness is
not claimed.

Reproduce with `make ui-health-page-closure`.
