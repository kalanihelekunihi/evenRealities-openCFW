# Independent review 2881

**PASS_SCOPED**; `accepted` remains false.

Authenticated flash and decoded-ITCM image hashes match inventory; all eight declared code-body hashes and candidate artifact hashes match. Isolated replay into a fresh destination passed 24 fixtures. The original initializer, output wrapper/dispatcher, operation-2 path, classifier, derivation, poll, delay and ITCM leaf execute without interception; only the power call is controlled. Derivation outputs 3/0, matching initialized stored values to avoid apply. Assertions cover gates, child order/args, bounds/status, 2,500 poll iterations when selected, delay/ITCM count, popped outputs, frame and PRIMASK. Scope is the stated gate/power/poll/mask fixture matrix with manually installed table slot and modeled peripheral readiness. It does not establish physical hardware, changing input state, apply behavior, dynamic caller/slot ownership, or general initializer behavior. accepted:false.

Candidate receipt SHA-256: `65e7a08a036d5028f51bf28304e356169bbab146746f16bb89e829d7eb0a5ee3`.
