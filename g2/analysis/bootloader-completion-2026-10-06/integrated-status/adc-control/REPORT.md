# ADC control and getters

Locked bootloader SHA f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5, original42ec0c..42ed60 (340 bytes). Reconstructed C and layouts: `g2/components/bootloader/initializer_callbacks/adc_control.c/h`. [Direct original/source comparisons](../adc-control-4cb522.json):279 PASS, all340 original body bytes visited. Native FP32 arithmetic/comparisons and FPSCR effects execute; no FP32 substitution. Error precedence, request truncation, window bounds/register order, raw trim flags, invalid calibration and cold/warm cache cases included. This is bounded fixture validation, not all inputs/hardware operation.

The original first reads handle+4 before the NULL/magic guard. Bad context returns2. Only the low8 request bits count. Request0 has no null argument guard: upper/lower at+4/+8 must be below0x100000 or it returns5. It writes upper4003802c, lower40038030 then enable-byte40038034. Unsupported request returns6. Requests1..3 reject null arguments with6 and require the float sentinel bitsc2f6e979 (-123.456), returning7 for mismatch (VCMP semantics include NaNs).

| Request | Input/output layout | Behavior |
| --- | --- | --- |
| 1 | input float+0; result+4; sentinel+8 | Celsius conversion with lazy intercept |
| 2 | raw trim words+0,+4,+8; sentinel/marker+12 | Copies20026fc0/fc4/fc8; stores markerbytefcc as raw32-bit0/1 (arbitrary rawbyte fixture also preserved) |
| 3 | raw offset+0,gain+4,zero+8,sentinel/zero+12 | Copies20026fe0/fe4; zeros tail; does not read validitybyte20027199 |

Readable ordered pseudocode for request1 (each operation rounds separately to FP32):

```c
input = args.input;
ate = trims.ate; measured = trims.measured; offset = trims.offset;
if (cache_at_20027028 == 0.0f) {  // +0 and -0; NaN skips
    cache = -290.0f;
    sum = fp32_add(measured, offset);
    cache = fp32_mul(sum, reload(cache));
    cache = fp32_add(reload(cache), ate);
}
result = fp32_mul(input, 290.0f);
result = fp32_add(result, reload(cache));
args.result = fp32_add(result, -273.15f);
return 0;
```

ATE/measured/offset are loaded even with a warm cache. Cache initialization performs three observable ordered stores. ADC init/reset zero2002702c, a different word; they do not invalidate20027028. The sequence test proves preservation under the fixture, not a measured hardware race. Application/CFW code must not equate API0 with valid calibration, or assume request3 exposes validity. The stock bringup calls request3 for logging; actual sample normalization and its validity gate remain to trace before adding another correction.

MMIO is mapped RAM, absent ROM reads in the chained initialization fixture are explicit controlled words/status. NULL preliminary read at address4 is mapped ROM in this test; actual fault behavior is not certified. Tests exercise FP rounding modes, default NaN and flush-to-zero fixtures, but do not prove arbitrary FPSCR/interleavings or physical conversion accuracy. The relocated source ELF is not byte identical or a standalone firmware image.
