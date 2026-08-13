# G2 SystemClose dependency boundary

Status: complete stock-object and provider closure over G2 2.2.6.10. No device
or flash operation is performed.

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
or evidence for the private producing commit. Its close/confirm/cancel/minimize,
scroll, animation, IMU-reflash, and display-lifecycle behavior remains
first-party UI policy and is not yet production-routed.

Forty direct entry sites, three stored pointers, no indirect body call, and no
strict-interior ingress close control-flow ownership. Eight unaligned raw words
that resemble interior pointers are not aligned callback or control-flow
records.

```sh
python3 openCFW/tools/analyze_g2_system_close.py
python3 -m unittest openCFW.tests.test_analyze_g2_system_close
```
