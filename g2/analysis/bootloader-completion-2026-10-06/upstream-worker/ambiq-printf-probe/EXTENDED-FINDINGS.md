# Expanded formatter comparison: exact upstream hypothesis rejected

`extended.json`:44 fixtures,20 matching,4 mismatching,20 blocked. The two actual mismatches are duplicated across translation off/on. `sinks.json`:16/16 native stock printf-wrapper comparisons match, including absent sink, integer arguments, callback bytes/count and translation off/on. Prior14 integer-parser fixtures remain preserved. These totals describe different fixture sets, not independent recovered functions or source coverage.

## Proven differences

For `%-8s` with `abc`, stock emits `abc` followed by8 spaces, count11. The SDK emits5 spaces, count8. Stock negative string width therefore behaves as trailing padding count in this case, rather than total field width.

For `%.2s` with `abcdef`, stock emits `ab`, count2. The SDK emits all6 characters, count6. String precision is a real incompatibility; upstream code visibly computes full strlen and copies through the terminator without applying precision.

Stock default precision is initialized to-1 in the parser (`0x415c3a`), whereas this SDK source initializes it to6. That is a static difference, not by itself a proved float-output mismatch.

The observed contracts can guide adaptation:

```c
/* Observed cases, not a complete parser implementation. */
emit_string("abc");
emit_padding(' ', 8); /* stock %-8s: 11 output bytes */
emit_string_prefix("abcdef", 2); /* stock %.2s: 2 bytes */
```

Boundary probes at width below/above length and precision0/negative/above-length are still needed before generalizing these two examples into full stock rules. No speculative adaptation was integrated.

## Matching bounded families

Tested string/default/right-width behavior, empty string, signed64 minimum, unsigned64 maximum, zero-padded64 hex and a32-bit→64-bit argument transition agree. ARM argument memory aligns64-bit values to8 bytes; host varargs represent the same scalar values independently. Tested `%*d` behavior agrees, but agreement does not mean standard printf star-width support. Newline translation flag is proven by stock literal at `0x415fe0` to address `0x200271c4`; the sink callback literal at `0x415fdc` resolves to `0x200270cc`, and buffer literal at `0x415ff0` to `0x20024cd0`. Literal format newline translation and string-contained newlines are tested separately.

Absent sink returns0 with no callback. Enabled sink receives synchronous formatted bytes once, and printf returns the parser count. Callback lifetime/reentrancy and physical transport remain untested.

## Exact float validation boundary

All20 float fixtures (10 values/formats ×2 translation states) stop at original `0x415f52`, bytes `b7 ee c0 0b`, decoded `vcvt.f32.f64 s0,d0`. The current Unicorn machine rejects that FP64 conversion. Fixtures cover finite, signed zero, NaN, infinities, width and precision, but none has a verified original float result. No conversion stub was added, and blocked fixtures are not counted as mismatches or passes. A suitable FP64-capable execution model or explicitly reviewed conversion model is required for this part of validation; hardware access is not necessary.

## Failure and truncation limits

This `printf`/`sprintf` API has no destination-capacity parameter. The downloaded `am_util_stdio_vsnprintf` is a separate source implementation: it returns0 when n≥its buffer size or formatted count≥n, otherwise copies exactly count bytes without adding a terminator in that copy loop. No stock counterpart was identified or executed here, so this is not a recovered firmware truncation contract. Null strings, overlong output and live concurrent sink failures are not run as native host tests, avoiding undefined host behavior masquerading as firmware evidence.

## Integration decision

Do not integrate the complete downloaded formatter as a stock replacement: two string contracts differ, and float behavior remains blocked. Preserve the verified `be4ede3b…` bootloader checkpoint. The next narrow work is string-boundary reconstruction plus FP64 validation, then a source adaptation under the retained BSD notice; only after direct comparison should it enter a new shared candidate and seven-case integration run. Existing14+20+16 matching fixtures establish a useful source-family shortcut, not exact upstream identity or byte equality.
