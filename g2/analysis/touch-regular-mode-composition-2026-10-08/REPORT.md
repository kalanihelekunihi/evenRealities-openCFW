# Regular/BIST mode composition without helper stubs

**1,080 full-mode comparisons passed**. Original `0x6ac0`, pin groups, critical sections and PDL configuration execute against independent mode/GPIO/CPU source plus unmodified public Infineon PDL `35f171...` configuration code. No function-entry stubs. GPIO, MSCLP, MRSS and factory trim bytes are synthetic.

Requested modes 0/1/2/3/4/5/6/8/255 are tested across prior modes 0/2/3/5/255, lock keys 0/2/255, IMO fields 0/3/6/7 and initial PRIMASK 0/1. MMIO/SFLASH access order, status, common/internal state and PRIMASK match. Request 7 is excluded because auto-dither's sensor-frame generator remains open; the binding explicitly documents this subset.

Regular setup configures electrode/shield/CMOD pins, clears common status bits `0x30` and active sense method, then calls PDL with key 2. PDL failure maps to `0x40`. It retains the prior mode but **does not roll back earlier GPIO/common changes**. Unsupported IMO field 7 can fail after writing the base configuration, whereas a key mismatch fails before PDL writes.

BIST mode 3 configures pins/CMOD without a PDL base frame. A subsequent different-mode request from prior state 3 is rejected, although requesting state 3 again succeeds.

Public Configure matches the 424-byte extent but differs in 24 bytes of loop layout: behavioral equivalence only. Exact compiled attribution elsewhere covers Capture/ConfigureScan. No physical frequency, analog acquisition or IRQ-concurrency claim.
