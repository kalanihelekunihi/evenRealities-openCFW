# Clock configuration children: recovered policy and state

Locked bootloader SHA-256 f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5, Thumb image base410000. Independent source: `g2/components/bootloader/initializer_callbacks/startup_clock_config.c`; no new vendor source import. The generic Ambiq printf adaptation and its retained BSD notice are unchanged.

| Stock body | Bytes | Newly explained behavior |
|---|---:|---|
|4216d4, class4|254|Validate0/48000000, generate/supply12-byte config, live compatibility, default/apply and cached state|
|4217d2, class5|422|Validate0/196608000/250000000, reference selection, compatible live reconfiguration and temporary clock requests/releases|
|421978, class6|184|Generate/supply12-byte config, reject active users, copy/cache/mark ready|

5,896 direct comparisons PASS, including a changed-argument negative control.848/860 original body bytes visited: class4's12-byte retry block421778..421784 is not reached because its native apply helper always returns0. Class5/6 bodies are entirely visited in this fixture matrix. Coverage is not an arbitrary-input/concurrency proof or whole-source percentage.

## Interfaces and layouts

The earlier dispatcher4222a0 truncates selector to8 bits and calls these children with two arguments: raw requested value and optional config pointer. Status5 rejects unsupported class4/5 values,7 rejects a missing required reference,3 rejects incompatible active use. Generator failures propagate. Numeric values are recorded exactly; physical units are not inferred from names alone.

The20-byte reference descriptor at2000007c has relevant words at offsets4 (primary reference),12 (class4 reference) and16 (secondary reference). Startup's descriptor `{0,0,0,8000,b71b00}` sets those to0,32768,12000000. Word0/offset8 roles are not established by these children.

| Class |12-byte cached configuration|Requested/cached word|Availability flag|
|---|---|---|---|
|4|20026fec|20027030|20000550|
|5|20026ff8|20027034|20000551|
|6|20027004|20027038|2002719a|

Class4 uses config word0 as the HFADJ register operand; default local words are25b800,0,0. Class5 config byte0 selects reference0/1; byte1's low2 bits and word+4's low29 bits are applied by the already recovered HF2 register leaf. Other stored fields remain opaque here. Class6 config byte0 selects the reference; remaining fields are the separate PLL generator/provider interface, not decoded by this batch.

Each accepted config copies12 bytes synchronously into fixed SRAM; caller/local pointer is not stored by these bodies. Generator implementations could have further behavior and remain outside that ownership statement. Critical sections save/disable/restore PRIMASK; this does not prove global DMA/task quiescence or atomic publication to every observer.

## Readable flow

```c
configure4(value, optional_config):
    reject unsupported value;
    if value != 0 and config absent:
        require reference_word_at_offset12;
        quotient = value / reference;
        insert quotient's low12 bits into default_config bits8..19;
    disable_interrupts;
    if class4_has_users:
        permit only compatible current/new values;
        apply supplied/generated word or restore default;
    else if value changes:
        restore default; clear active and callback pointer;
    on success: copy config if nonzero; cache value; mark available;
    restore_interrupts;

configure5(value, optional_config):
    reject unsupported value; select/validate reference or generate config;
    disable_interrupts;
    if users and current/new values are outside the0/250000000 pair: return3;
    on success: copy config if nonzero; cache value; mark available;
    restore_interrupts;
    if compatible users were present:
        request temporary reference clock as user36;
        disable_interrupts; recheck users;
        apply cached config/default or skip application if users disappeared;
        release opposite/both reference clocks as dictated by outcome;
        restore_interrupts;

configure6(value, optional_config):
    select/validate reference; generate config if absent;
    propagate generation failure;
    disable_interrupts;
    reject any active class6 users with3;
    otherwise copy12 bytes, cache value, mark ready;
    restore_interrupts;
```

Class5 ignores request/release return codes and rechecks users after requesting a reference. A register-apply failure would not automatically restore cached config/value. Current native apply helper always returns0 for its nonnull cached pointer. Tests synthetically remove users at the request boundary to prove the cleanup branch; no real scheduling race is claimed.

Startup calls class4/5 with value0/configNULL. With no users and cached0, they mark availability; this is not immediate oscillator activation. This distinction matters for CFW clock-policy changes and for interpreting startup.

## Native and modeled boundaries

Original count/critical/copy, class4 apply/default, and class5 apply/default children execute natively. SRAM is compared after execution; the MMIO-only recorder avoids the independently reproduced global-SRAM-hook defect, with no copy-answer stub.

Two frequency generators remain explicit dependencies:426c24 (HF2 generation),427160 (PLL generation). Direct tests model their outputs/status equally. Existing clock request/release helpers bind real source in the shared candidate, but their side effects are injected in the dedicated configuration matrix;129 separate shared clock cases PASS. The synthetic request can remove class5 users to exercise revalidation. Timing, live IRQ/task scheduling, post-wake ownership and physical lock/drain remain unverified.

Candidate e1049dc3… links the three children and native HF2 apply leaf, with642 inputs/164 objects frozen. Direct5,896 config,271 native-copy wrappers,64 native descriptor-copy supplement,1,778 parser/288 sink,129 clock and affected logger/kernel regressions PASS.480 alignment mappings PASS. Seven-case promotion is recorded separately after completion; prior8ba02bde… checkpoint is preserved.

## Verified shared checkpoint

All7 cases PASS on e1049dc3f5b60479f3ca4f665fab62e11a495f8629f806238741b2b7661acac3.642 inputs/164 objects remain unchanged and exact copies are preserved.480 alignment mappings;28 numeric aliases at28 addresses,21 in OTA;42 segments;zero receipt source mismatches. Previous8ba02bde/be4ede3b and intermediate snapshots remain preserved. See `../../integrated-status/same-image-validation-e104.json`. All heavy validation finished before07:00UTC.
