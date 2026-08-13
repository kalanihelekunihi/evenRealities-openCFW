# G2 EvenAI text-stream service recovery

Status: read-only, fail-closed closure of stock 2.2.6.10
`app\gui\EvenAI\text_stream_service.c`.

## Result

The single 116-byte baseline anchor was only `ensure_text_capacity`. The full
translation unit is `[0x00552B30,0x005537CC)`: 26 functions / 3,188 reachable
instruction bytes and three small compiler pools / 40 bytes, for 3,228
physical bytes. Baseline Ghidra defined eight functions and missed 18,
including the 340-byte `animate_text` timer callback. That callback has no raw
stored pointer: the timer creator forms its Thumb address PC-relatively at
`0x00552FD0`, which is now pinned as an explicit callback-construction edge.

The service allocates a 48-byte state object, a mutex, and two initially
512-byte NUL-terminated UTF-8 buffers. Capacity doubles or rises to a caller's
minimum through the synchronized realloc seam. Replace, append, immediate,
and animated update paths maintain current/pending lengths and invoke the
caller callback stored at offset `0x18`. The periodic timer defaults to 100
ticks and emits one whole UTF-8 code point per tick by recognizing 1-, 2-, 3-,
and 4-byte lead sequences. A related global path decodes and manages four
generic-animation presets.

Sixty-five image-wide direct BL sites reach exact entries; 34 are external.
All 1,361 instructions, 144 direct body calls, seven indirect callback sites,
the one PC-relative callback construction, path and diagnostic strings,
adjacent boundaries, and the absence of strict-interior or unrecovered direct
targets are authenticated.

## Dependency result

No third-party implementation is embedded. The 113 direct external calls
terminate at previously admitted seams:

- 39 exact CMSIS-FreeRTOS v10.5.1 timer/mutex calls at commit `d213f261…`;
- 17 LVGL object/style calls within the authenticated 9.3-compatible interval;
- 10 EasyLogger diagnostic calls at selected commit `a596b264…`;
- nine synchronized allocation calls over the admitted TLSF v3.1-compatible
  source interval;
- five `pb_istream_from_buffer` calls over the admitted nanopb interval;
- 22 bounded IAR DLIB memory/string calls; and
- 11 bounded first-party generic-animation/string-provider calls.

The object therefore adds no dependency family and no narrower version or
commit discriminator. The exact private source and producing commit remain
unavailable, as do the exact generating LVGL, nanopb, TLSF, and IAR checkouts.
The service is not production-routed.

## Reproduction

```sh
make text-stream-service-closure
```

The target performs authenticated read-only analysis and tests only.
