# ADC sample correction, enumeration and lifecycle

Locked bootloader SHA f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5. New reconstructed source/interfaces: `g2/components/bootloader/initializer_callbacks/adc_samples.c/h`. Seven bodies total776 original instruction bytes: activation42ed60(64), trigger timer enable42ebaa(56), disable42ebe2(42), command42eff4(32), deactivation42eda0(86), sample correction42ee00(108), enumeration42ee70(388). Alignment/literal gaps are excluded. [Ownership/provenance](../adc-samples-source-ownership-8287c7.json), [disassembly](original-disassembly.txt), [988 original/source comparisons](../adc-samples-8287c7.json) PASS with all776 body bytes visited on image8287c7b86fea2f84996c517fa1d82b27fd23dd780d923d38db8376bf93e17014. No ADC FP32 or clock-release success stubs in these direct comparisons. This is bounded synthetic validation, not arbitrary inputs or physical behavior.

## Numerical correction

Unlike request3 getter, correction first checks validitybyte20027199, then low8 enable argument. Either zero returns the entire input word unchanged, without reading the correction pair. Otherwise, individually rounded native FP32 instructions execute:

```c
scaled_integer = (((word >> 6) & 0x3fff) * 1190) >> 12;
x = VCVT_F32_U32(scaled_integer);
x = VDIV(x, VSUB(1.0f, gain_at_20026fe4));
x = VMLA_nonfused(x, offset_at_20026fe0, -1000.0f);
x = VMUL(x, 4096.0f);
x = VDIV(x, 1190.0f);
word = (word & 0xfff00000) | ((VCVT_U32_F32(x) << 6) & 0x3ffff);
```

The result mask retains only12 corrected bits6..17, clears bits18..19 and low6, and preserves metadata20..31. There is no explicit finite/range/clamp check. Tests compare original/source return bytes and FPSCR for normal/zero/negative/NaN calibration, zero divisor and rounding/FZ/DN fixtures. This records Unicorn agreement, not physical FPU certification. Raw nonzero calibration words qualifying during initialization need not represent finite safe calibration; API0 and pair getter output still do not prove validity. Firmware sample conversion may already apply the pair; apps must trace which sample path they consume before applying another correction.

## Enumeration interface and read order

`enumerate(context, full_sample, buffer, &count, output)` receives maximum count in `*count`, replaces it with produced count, and writes `{sample, slot}` records,8 bytes each. It reads count before context/output validation. Invalid context returns2; null output returns6 without zeroing count. Count/null-readable pointer guards are not added by faithful reconstruction.

With `buffer == NULL`, each iteration reads one live FIFO word4003803c, identifies slot from bits28..30, reads that slot's channel-select nibble(bits8..11), then enables correction unless selected input is8(TEMP). It writes slot first then sample. Low8 full_sample nonzero selects corrected word&0xfffff; zero selects bits6..19. It increments count, stops when FIFO count bits20..27 are zero or requested capacity reached. Hardware pop/empty effects are not established by the explicit perread word queue in these tests.

With a supplied buffer, it first reads all eight slot configurations and builds a temperature-input mask. Each iteration reads the input word once for slot and again for sample, strips metadata, conditionally corrects, then writes shifted14-bit sample and retained slot. It ignores full_sample in this branch. Test observations compare buffer/slot/FIFO read order. Mutable buffers between these reads are not proven safe.

Both branches have do-while behavior: requested count0 still processes **one** record. Callers of this raw reconstructed interface need readable input/count and room for that record; it is not a zero-count probe API. No speculative firmware fix or memory-management patch is applied.

Pinned Apollo510 SDK5.1 confirms CHSEL TEMP8 and BATT9, ADSEL averaging bits24..26, and FIFO6-bit fractional layout; [SDK evidence](../adc-configuration/sdk-evidence.json). The bypass is for the internal temperature sensor, not averaging mode8.

## Lifecycle boundaries

| Entry | Proven register/metadata behavior |
| --- | --- |
| activate42ed60 | If context flagbit25 alreadyset, returns0 without enabling ADC. Otherwise sets CFG40038000 bit0, then context bit25. |
| enable42ebaa | Requires CFG bit0 or returns7; sets **INTTRIGTIMER40038040 bit31**, not interrupt enable. |
| disable42ebe2 | Clears INTTRIGTIMER bit31; does not change interrupt enable40038200. |
| command42eff4 | Writes37h to software trigger40038008. |
| legacy adc_normalize42eda0 | Deactivates: clears CFG repeatbit2 then ADC-enablebit0; clock selector3→0; calls native clock_release(4,15); clears context bit25 and returns0 ignoring release status. |

All lifecycle entries first read context+4, then validate null/magic; error2 precedes peripheral effects. Deactivation does not itself clear timer enable; stock caller separately invokes disable first. An already-set metadata bit25 with CFG bit0 clear makes activate return0 while enable returns7 in the tested synthetic state. These are metadata/register semantics, not verified physical faults.

Native reused clock release422364 and class4 user bitmap/critical/HFADJ children execute. Direct fixtures cover absent user15, sole user15, another remaining user, and initial PRIMASK0/1; remaining-user case retains HFADJ, sole-user case disables it. No allocator/free/drain, pending IRQ acknowledgement, scheduler stop, callback cancellation or quiescence barrier is shown by these routines. Prior external ROM/factory and real IRQ/task evidence boundaries remain.

Seven-case startup integration supplies explicit FIFO words representing0,0,3200 with count1 and uses synthetic ready register bit20. This replaces the former whole-enumeration return stub; it does not model physical conversion timing, actual FIFO empty behavior or analog calibration. See the exact-image checkpoint report for completed full-case results; do not infer shared-case PASS from these direct comparisons alone.

Next remaining bootloader ADC providers are profile transfer42f020 and apply-profile42ea68 (including clock request4222f0); then service/post-bringup/kernel/runtime/source/layout closure. Complete ADC init/reconstruction, source-complete firmware and byte equality are separate claims.
