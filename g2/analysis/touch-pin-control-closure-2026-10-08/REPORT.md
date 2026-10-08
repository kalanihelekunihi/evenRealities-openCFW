# GPIO/HSIOM electrode, shield and CMOD control

Independent source in `../../components/touch/pin_control_offline/` reconstructs `0x5fc6`, `0x6044`, `0x6078`, `0x60ea` and the GPIO/HSIOM leaf semantics. **216 direct-pin and 72 complete-wrapper comparisons passed**, including ordered MMIO values and PRIMASK during every access. No function-entry stubs. Registers are synthetic.

Only valid pins 0–7 and drive/HSIOM values 0–15 are covered; stock breakpoint assertions for malformed inputs are excluded. HSIOM address is `((((port+0xbffc0000)>>8)+0x400200)<<8)`, with four bits per pin. Drive uses three bits per pin at GPIO+8 and an input-disable bit at +`0x18` from drive bit 3.

With mux zero, disconnection occurs before drive configuration; otherwise drive configuration precedes mux selection. The complete pin update, including analog ownership at +`0x24`, occurs in a critical section; prior PRIMASK is restored. Physical routing/glitches are unverified.

Electrode descriptors have stride 8: port pointer +0, pin byte +4. Count is common-config u16 +12; array pointer is context +20. GPIO SET +`0x40` or CLEAR +`0x44` follows each pin update. Shield count is common byte +44, array context +24, and shield output always clears. CMOD pins come from channel-config port/pin offsets +8/+12 and +16/+20; no separate output write occurs.

Regular mode uses drive 9, mux 0, analog ownership 1 and output 0. Pinned Infineon 6.10 LP source corroborates semantics, without uniquely identifying the producer revision. No physical pin writes or firmware patch were performed.
