# Battery ADC filter uses a C workspace

`native_battery_filter.c` now uses a volatile 16-byte C workspace containing the sample word and five halfword samples. Fixed registers, empty assembly and stack-word helpers are removed. The whole unit has no inline assembly or register bindings. The used sample halfword and sample array start at zero; unused upper scratch bytes are not API inputs.

The filter still opens the current ADC handle, takes five samples, clears the sample halfword after each read, chooses RTOS or busy delay from the live runtime mode byte, and closes the current handle. It rereads the volatile sample array after close, subtracts the two lowest values from the accumulated sum, divides by three, narrows to a halfword and performs the original unsigned wrapping calibration products and division.

The [receipt](battery-filter-pure-c-review.json) records 2,816 stock/C cases. They cover constant, extreme, duplicate and mixed samples; no/partial/full ADC writes; changing handles and delay modes; raw provider statuses; sample mutations during delays; and array mutations during or after close. Each run takes five reads and five delays. Requests, handle/call order, low sample bytes, final sample array/runtime state, result, balanced stack, preserved registers and masks agree. Four controls with incorrect trimming, calibration scale, sample clearing or delay argument are rejected.

REA raw-byte evidence identifies stock entry `0x91184`. Replay uses code hooks without memory-read hooks. ADC, delay and registry boundaries remain modeled. Private pointers are normalized, and unused upper sample bytes/private frames/scratch-register outputs are excluded. Physical ADC calibration, delay timing, arbitrary faults and concurrency remain unverified. No byte identity or complete firmware image is claimed.

The normal report is `build/sources-goal-r1-battery-filter-pure-c/report.json`: 727 units compile without failures or duplicate strong symbols. Imports remain 178 application and 34 bootloader. Only the battery filter object changed; 726 objects remain unchanged. Both source manifests pass `make sources-check`.
