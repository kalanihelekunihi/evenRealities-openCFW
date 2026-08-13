# G2 Translate UI dependency boundary

Status: complete stock object and reusable-provider closure; first-party source
reconstruction remains open. No device or flash operation is performed.

## Result

The retained `app\gui\translate\translate_ui.c` object is exactly
`[0x0059D380,0x0059E9E2)`: 5,730 physical bytes containing 29 linked function
bodies / 5,288 executable bytes and 442 bytes of alignment, literal pools, and
callback descriptors. Seven Ghidra/path anchors cover 1,568 bytes; direct-call,
stored-entry, and source-order recovery adds the other 22 bodies.

The preceding ownership is now cleanly separated:

- `[0x0059D244,0x0059D350)` is the newly source-recreated IAR DLIB
  `frexpf`/helper/`ldexpf` tranche;
- `[0x0059D350,0x0059D37C)` is the already source-owned CRC-16/XMODEM leaf;
- four alignment bytes end at the Translate UI start; and
- `0x0059E9E2` begins the independently closed `translate.c` object.

The object has 1,942 reachable instructions, 367 direct calls (21 internal,
346 external), 41 direct entry calls, 13 stored exact-entry pointers, and zero
strict-interior ingress. Its one indirect BLX at `0x0059DD54` loads the callee
from offset `+4` of a bounded first-party operation record and passes the
record-specific context; it is not an unclassified library dispatch.

## Provider closure

| Provider | Edges | Result |
|---|---:|---|
| EasyLogger | 175 | selected 2.2.99-compatible source `a596b264…` |
| LVGL | 125 | selected 9.3-compatible ceiling `344c7c31…` |
| IAR DLIB memory runtime | 10 | bounded/source-recreated; EWARM 9.20+ floor, 9.60.2 leading candidate |
| CMSIS-FreeRTOS | 2 | exact v10.5.1 source `d213f261…` |
| first-party UI/service functions | 34 direct + 1 indirect | bounded neighboring Translate, prompt, animation, display, and service graph |

There is no embedded third-party implementation body, new dependency family,
or additional version/commit discriminator. The first 268 bytes previously
adjacent to this object were the only new reusable-code gap; their exact
clean-room admission is documented in
[`iar-dlib-frexpf-ldexpf-recovery.md`](iar-dlib-frexpf-ldexpf-recovery.md).
The remaining Translate UI work is first-party behavior reconstruction, not
third-party utility closure.

## Reproduction

```sh
python3 tools/analyze_g2_translate_ui.py
python3 -m unittest -v tests.test_analyze_g2_translate_ui
```
