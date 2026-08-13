# G2 firmware event-loop dependency boundary

Status: complete stock-object, provider, and production-source closure over G2
2.2.6.10. No device or flash operation is performed.

## Result

`framework\fw_event_loop\fw_event_loop.c` occupies
`[0x004764E0,0x00476CBC)`: six functions / 1,806 executable bytes, two bytes of
alignment, and a 204-byte literal pool, totaling 2,012 physical bytes. Ghidra
found five path-anchored functions. The missed 108-byte worker at `0x00476680`
is recovered from the retained CMSIS thread descriptor and complete source
order.

The object is already source-replaced in production. The overlay routes all
six stock entries to `components/apollo_main/core_overlay/event_loop.c`, whose
SHA-256 is
`e1ac9d2f18f411d712b771a3b698c89de9a340843bc26294e629e14b6e915ccc`.
Existing host-oracle tests exercise initialization, immediate queueing,
callback dispatch, delayed registration, timer expiration/rescheduling, and
removal.

## Provider closure

The 108 direct calls split into four local and 104 external calls:

| Provider | Calls | Provenance |
|---|---:|---|
| EasyLogger | 80 | selected source-equivalent commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| CMSIS-FreeRTOS | 20 | v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` over FreeRTOS-Kernel `def7d2df2b0506d3d249334974f51e427c17a41c` and CMSIS_5 `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` |
| FreeRTOS critical port | 4 | exact admitted critical enter/exit bodies from kernel commit `def7d2df…` |

The worker has one indirect call at `0x0047668A`. It is bounded to the callback
and argument dequeued together from an eight-byte event record. There are 198
direct entry sites, no stored entry pointer, and no strict-interior ingress.
One unaligned raw word at `0x0064CE7B` happens to encode interior address
`0x00476AFE`; it is not an aligned callback or control-flow edge.

No scheduler, allocator, logger, or other reusable implementation is hidden in
the first-party object. It adds no version discriminator and cannot identify a
private G2 producing commit; all third-party behavior terminates at sources
already admitted into OpenCFW.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_fw_event_loop.py
python3 -m unittest openCFW.tests.test_analyze_g2_fw_event_loop
```

The analyzer authenticates every stock function, physical boundary, path
reference, direct and indirect call, ingress site, selected provider commit,
and all six production replacement routes.
