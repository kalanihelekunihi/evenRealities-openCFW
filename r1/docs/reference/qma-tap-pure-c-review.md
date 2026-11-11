# Ordinary C QMA6100 tap configuration

`r1/src/application/runtime/native_qma_configuration.c` replaces the tap entry's naked wrapper and private worker with one ordinary C implementation of stock `0x872e4`. Five register bytes now use initialized local storage instead of old stack bytes. All accesses that must remain live between provider calls are volatile. No persistent state is added.

The function retains five reads, three fixed setup writes, axes-mask update and the route-dependent writes. Axes use their low byte for masking and bit zero for the additional axis route. Routes zero/one remain distinct; other full-word route values return the first axes-write status. All read statuses remain ignored and the final selected write result is preserved. The zero initialization is a deliberate unwritten-read policy, not equivalence to arbitrary old stack data.

REA bytes match the official artifact. Direct execution passes **37,134 stock/C comparisons** across all axes bytes, both valid routes and invalid full-word routes, enable words, input bytes and raw retry return words. Callback tests mutate earlier explicitly supplied read buffers between writes, verifying live reloads during the function's lifetime. Another **72 unwritten-read cases** check zero fallback independently of caller stack seeds.

An additional **846 stock/C comparisons and 72 fallback cases** execute the actual C retry transport and delay-unit logic, with modeled bus results and the cycle-delay primitive. Register/data traffic, retry outcomes and tap results agree. Both fixtures verify caller stack, callee-saved integer/FP registers, SP and interrupt masks while modeled callees overwrite caller-saved registers. Five compiled defects are rejected: wrong axes mask, wrong axis gate, lost route one, reversed enable polarity and wrong scratch fallback.

The open-toolchain report `build/sources-goal-r1-qma-tap-pure-c/report.json` compiles all **855 units** and completes both relocatable compositions. All **844 other nongenerated objects** remain unchanged. The normal QMA configuration object equals both executed probe objects. Six other functions in this unit retain their exact bytes and relocations; cold sensor state and axis defaults also remain identical. Imports remain **61 application / 22 bootloader**. R1 manifest validation passes and manifest/source-plan selections are unchanged.

Both `native_qma*.c` runtime units now contain no inline assembly or naked functions. The architectural cycle-delay primitive remains assembly elsewhere. Physical tap/sensor operation, bus/delay timing, final application linking/startup, provider overruns, arbitrary private-frame aliases, APSR, faults/concurrency and byte identity remain unverified or excluded.

[Machine receipt](qma-tap-pure-c-review.json) binds sources, REA, reports and ignored probe evidence under `build/goal-r1-qma-tap-pure-c/`.
