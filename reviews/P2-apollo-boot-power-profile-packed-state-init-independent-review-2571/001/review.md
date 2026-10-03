# Independent review 2571

**Result: PASS_SCOPED.**

The bound packet is `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-profile-packed-state-init-2570/001`. Receipt and artifact hashes, source image, body span `[0x42BDF0,0x42BF4E)`, and the four literal words match. I reran an isolated copy; all 72 original-instruction fixtures passed.

The independent Python oracle applies explicit bit insertion to the original 16/4/1-word controlled payloads and checks all 112 state bytes. The tested routine copies words into offsets 68..80 with only low-seven-bit replacement, applies the stated averaged/direct seven-bit fields and bit-28 fields, copies fields into word 52, and sets word 104 bits 20..25 to 31 while preserving other bits. Guard and each read-error stage verify call counts/arguments, prior writes retained without rollback, dispatch installation only after success, returned error/status, SP and high registers.

The information-read callee and runtime callback remain controlled here; their separate reports do not make this composition original-child execution. Payload seeds and guards are synthetic and stable. Physical contents/mapping, concurrency, installation ownership and other profiles are unresolved. Private evidence only; accepted:false and no canonical admission.
