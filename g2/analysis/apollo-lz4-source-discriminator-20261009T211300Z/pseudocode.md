# Hash-bound raw LZ4 and caller contract

Locked Apollo raw image SHA19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701, base438000. Selected ranges: read_variable_length54EE90..54EF06(118), generic54EF08..54F338(1072), safe54F338..54F356(30):1220bytes. Five local helpers54EE18..54EE8C and actual copy/move bodies439BE4..439C8A /439710..4397A6 execute original bytes. Literal dependencies remain mapped from full authenticated raw image; text-only envelopes are not a complete firmware link closure.

Safe API takes(source,destination,signed compressedSize,signed capacity). Wrapper supplies generic stack flags `[fullBlock,noDict,destination,NULL,0]`; no unsafe-fast API or frame parsing is assumed. Generic rejects null source/negative capacity; full zero-capacity decode accepts only compressedSize1/token0. Error is `-(input_cursor-source)-1`; success is output_cursor-destination. Bounded12 fixtures validate selected acceptance/return positions, not every branch or negative-size contract.

```c
/* Recovered outer caller4E0C0C..4E0C34, synthetic read-only execution only. */
int32_t caller(const void *src, int32_t compressed_size,
               void *dst, int32_t capacity) {
    if (!src || !dst || !compressed_size || !capacity) return 0;
    int32_t result = stock_LZ4_decompress_safe(src,dst,compressed_size,capacity);
    return result < 1 ? 0 : result;
}
```

The outer caller therefore cannot expose exact negative error positions and conflates encoded empty success with rejection/precheck. Its navigation/app root is not established: historical emulator caller56192E bytes disagree with this locked target. The independently found4E0C28 BL is bound; no emulator callsite bytes were substituted.

Generic sequence behavior follows literals, little-endian16-bit offset and optional match length. Short-offset overlapping copy expands repeated output; malformed paths may leave partial writes inside capacity. Preserve exact signed returns and discard rejected output. Guard boundary is declared capacity, not returned length; wild-copy in-capacity tails do not prove overflow. Stock zero-offset fixture returns26: oneA,20zero match bytes, fiveabcde. Official spec says offset0 denotes a corrupt block; acceptance is decoder tolerance, not permission for an app encoder to emit it.

Reusable app/CFW guidance: use standards-compliant raw blocks (not frames); represent a genuine empty raw block with token00 when calling the safe API; keep host offset validation strict; retain a separate signed decoder status if an interface needs error diagnostics rather than forwarding the outer caller's0. Do not infer navigation ownership/lifetime or physical scene behavior from this decoder contract.
