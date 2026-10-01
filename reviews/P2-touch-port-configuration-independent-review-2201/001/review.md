# Independent review 2201

**Result:** PASS_SCOPED.

The source and receipt files match their declared hashes. The independently sliced body [0x5FC6, 0x6044) is 126 bytes and matches its body hash; independent Thumb/M-class disassembly matches the candidate listing.

An isolated replay regenerated all 288 fixtures exactly. It varies every pin 0–7, modes 0/1/`0xFFFFFFFF`, enable 0/1, initial PRIMASK 0/1 and three initial port words. The replay verifies child order and arguments while PRIMASK is 1, the single full-word update at port+36, PRIMASK restoration, R4/R8 and SP. Decoded control flow agrees with the pseudocode: mode zero calls 5CF8 then 5D34; other modes reverse the order and pass the mode to 5CF8. The helper reloads the enable stack argument, computes `(1 << pin) & 0xFF`, and sets or clears that bit at port+36. Original 4492/449A save and restore PRIMASK.

**Limits:** 5CF8 and 5D34 are controlled. Invalid-pin BKPT continuation, child effects, physical port behavior, aliasing and concurrency remain unverified. No canonical admission is made.
