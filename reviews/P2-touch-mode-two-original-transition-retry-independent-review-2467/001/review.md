# Independent review 2467

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-mode-two-original-transition-retry-2466/001`. Receipt SHA-256 `8750241977be56e97e0f27c47a2778ef484f745406cd1fa71c4c769ca35e0919`; all four declared artifact hashes match, and all ten listed spans hash against the pinned source image.

The isolated replay passed all 320 cases. Each case performs two original request-2 dispatcher calls on the same retained memory. For supported selectors 0/3/6, the first call transitions to mode 2 and the second equality path returns zero without repeating setup, pin, loader, or destination writes. Unsupported selectors repeat the failure transition on the second call, preserve the old mode, and return 64 again. Assertions check the boundary between calls, exact repeated call/write sequences, final state/status, port configuration, PRIMASK, and R4–R11/SP. No firmware function is intercepted.

**Limits:** Source, factory, and MMIO values are modeled. Physical effects, concurrent mutation, selector/version changes between calls, and integration with the measurement path are not established. Candidate extent and literal/table ownership limits remain. Private evidence only; accepted:false, no canonical admission.
