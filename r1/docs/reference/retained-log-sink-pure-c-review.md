# R1 retained diagnostic sink in ordinary C

The sink at `0x7f030` now uses `va_start`/`va_end` with the existing typed C formatter. Its assembly register-save bridge and exported frame worker are removed. Null-format handling, cold initialization, marker binding, signed available capacity, live cursor/buffer reloads, newline, uint16 cursor behavior and stdout return remain native.

All 308 comparisons through the actual C formatter pass, including mixed 32/64-bit integer, binary64 and string arguments across the register/stack boundary, cold/warm contexts and buffer boundaries. REA matches the locked 146-byte stock body; every instruction byte executes. Eight compiled defects are rejected. Another 180 controlled callback comparisons verify partial writes, negative/zero/positive returns, uint16 cursor wrap and live cursor/buffer mutations.

The normal build compiles 862 units with 63 application and 22 bootloader imports, without failures or duplicate strong symbols. The other 851 prior nongenerated objects are identical. Manifest, source plan and persistent state are unchanged; R1 source checking passes.

Copy/fill, crash initialization and stdout are modeled; the 180 callback cases also model formatting. For oversized formatter returns, stock stdout spans can escape the retained buffer. These cases compare address/length but exclude unrelated bytes outside the buffer. This conversion preserves the existing policy and does not claim to harden it. Private frames, caller scratch, APSR and exhaustive formatting semantics are excluded. Physical retention, RTT transport, final application linking and boot remain unverified.

See the [machine-readable receipt](retained-log-sink-pure-c-review.json) for hashes and results. Probes are under `build/goal-r1-retained-sink-c/`.
