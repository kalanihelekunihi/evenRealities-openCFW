# Pin configuration guard and mutation probes

Eleven original-instruction fixtures cover both null returns, seven initial breakpoint conditions, and two post-helper configuration mutations. Each breakpoint fixture stops immediately before the original BKPT instruction; it does not turn a breakpoint into an ordinary return or model debugger behavior. Initial invalid fields produce no helper calls or MMIO writes. Null paths return005A0001 with frame restored.

A controlled last helper changes configuration+16 or+20 to2 after initial validation. Actual later reloads reach respectively BKPT8F58 or8F72. The latter occurs after the bit24 write, preserving that partial MMIO effect. The former makes no MMIO write. This demonstrates fresh validation and partial effects; physical mutation timing, bus semantics and breakpoint continuation remain unresolved. Prior1230 is unchanged. No canonical admission or C implementation.
