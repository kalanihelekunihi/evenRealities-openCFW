# SpO2 calculation control flow in C

The [cached-result encoder](goodix-spo2-result-encode-c-review.md) now executes in C for partial/error windows. Eleven later core stages remain unfinished.

The [batch-accumulation review](goodix-spo2-batch-c-review.md) adds actual C window accumulation and averaging, with two-window lifecycles and the real frame pipeline. Incomplete-window status3 is preserved. Twelve later processing stages remain unfinished.

The [numeric-decoder review](goodix-spo2-decode-c-review.md) adds actual C decoding and nominal TIA gain state. Real frame/core/assembler/decoder replays agree with stock; fixed power calls become verified exact constants. Thirteen later processing stages remain unfinished.

The [channel-assembly review](goodix-spo2-assemble-c-review.md) adds the real C assembler and parity helpers, with live enable/PPG integrity effects checked through the C core. The remaining numeric decoder is explicit as `r1_goodix_spo2_decode`; the complete computation engine is still unfinished.

The [packet-layout correction](goodix-spo2-packet-layout-c-review.md) makes the enable mask and following PPG samples one C object. It preserves the assembler12-byte scan and live integrity-write aliasing that the earlier four-byte boundary checks did not cover. The deeper processing stages remain unfinished.

`native_spo2_calculate.c` implements the682-byte native core control flow at0x6e838. It shares the existing context and C polynomial, preserves allocation/error timing, counter wrap, elapsed count and live context reloads, and adds no persistent state.

Calibration preserves raw float-bit thresholds, signaling comparisons and truncating metric conversions. Defined integer decoding handles saturation, NaNs and subnormals; ARM compiler intrinsics preserve floating-point status without inline assembly or undefined casts.

**1,821 stock-versus-C comparisons pass**, executing all682 native instruction bytes. Full active FPSCR and RAM snapshots agree, including context changes during callbacks, error paths, exceptional metrics, wrapped sizes and all rounding/FZ/DN combinations. Independent call-order, status, scratch and allocation-size oracles pass. Saved registers, stack and masks agree; source cannot execute stock. Twelve compiled defects are rejected. An exploratory NaN-invalid mutation was redundant after the preceding signaling comparison and is retained outside that count.

The polynomial bodies execute actual C/native code. Fourteen processing stages and allocator/free/clear ports are modeled. Actual allocator lifecycles, inference, hardware sampling, allocation failures, concurrency and cold FPU behavior remain unverified. A separate20,832-case controlled instruction replay supports the conversion primitive; it is not another stock-function admission.

All **901 R1 units** compile and compose without failures or duplicate strong symbols. The tested object equals the normal object;890 prior nongenerated source/object pairs and source-plan/cache files are unchanged. Replacing the aggregate core with14 explicit unfinished stages increases application imports78 to91; bootloader imports stay22.

This is control-flow reconstruction and relocatable composition, not a complete SpO2 engine or bootable firmware image.

[Machine-readable evidence](goodix-spo2-calculate-c-review.json) records exact contracts, provider addresses and hashes.
