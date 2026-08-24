# G2 SystemClose dependency boundary

Status: complete stock-object/provider closure and production source routing
over G2 2.2.6.10. No device or flash operation is performed.

`app\gui\SystemClose\systemClose.c` occupies
`[0x00469BF4,0x0046B0EC)`: 20 functions / 4,960 executable bytes and 408
alignment/literal bytes, totaling 5,368 physical bytes. It begins exactly at
the end of the closed Silent Mode object. Its final UI-lifecycle function is
`[0x0046AEEA,0x0046B004)`; this corrects the old service-settings boundary,
which had mistaken those 282 bytes for part of SystemClose's terminal pool.

Ghidra found only five functions. Direct-call topology, three stored entry
pointers, complete source order, and 27 path references restore fifteen more.
The exact retained names recover the common-data handler, page-event handler,
selection animation callback, selection/scroll/click handlers, option builder,
reflash handler, and UI lifecycle. Five compact pathless helpers implement the
bounded event FIFO.

The 296 direct calls split into 25 local and 271 external calls:

| Provider | Calls | Provenance |
|---|---:|---|
| EasyLogger | 130 | selected source-equivalent commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| LVGL and its G2 display integration | 99 | compatible selected commit `344c7c318047b7348e1be8572a9fd4260c251cfa` |
| IAR DLIB memory runtime | 5 | bounded image-local runtime seam; exact release unobservable |
| first-party display/sync/page policy | 37 | private G2 code over already bounded providers |

There is no CMSIS-FreeRTOS, allocator, protobuf, Cordio, or other reusable
implementation in the object. It adds no dependency, version discriminator,
or evidence for the private producing commit.

Forty direct entry sites, three stored pointers, no indirect body call, and no
strict-interior ingress close control-flow ownership. Eight unaligned raw words
that resemble interior pointers are not aligned callback or control-flow
records.

`components/apollo_main/core_overlay/system_close.c` independently implements
all twenty callable entries. Twenty guarded Apple-Clang redirects replace all
4,960 stock function bytes. The selector-isolated Cortex-M55 output is 2,804
text bytes plus 22 alignment bytes with 118 strict relocations; the 408-byte
official alignment/literal remainder stays stock-carried. Host tests cover the
bounded FIFO, common-data allowlist, role-gated page actions, layout, scroll and
animation queuing, confirm/cancel/minimize policy, IMU reflash dispatch, page
factory, and display lifecycle.

The canonical overlay/component/package sizes are 228,222 / 3,751,618 /
4,530,112 bytes with SHA-256 values `ee0ced13721b...cda491`,
`c6ac27de8a0e...fca42`, and `7cd4e6760f03...dc2c8`. The 2,503,413-byte flash
plan contains 3,589 placed, two unresolved, five container-only, and six
protected regions. No package was signed or flashed. Live close-page display,
selection animation, IMU reflash, shutdown/minimize transition, and peer
synchronization evidence is blocked: the authorized right temple is
nonresponsive and the left temple must remain stock. This closes the software
gap only; it is not a firmware-completeness claim.

```sh
python3 openCFW/tools/analyze_g2_system_close.py
python3 -m unittest tests.test_system_close_candidate tests.test_analyze_g2_system_close
```
