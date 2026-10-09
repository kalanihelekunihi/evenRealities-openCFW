# Enclosing UART power composition and actual callback selection

**408 original-instruction/source compositions PASS** with identical ordered MMIO read/write traces, callback events, saved/restored PRIMASK, final pending state, return status and delay arguments. The final native ELF binds all selected source hashes in [receipt](reproduction-receipt.json); [results](results.json) include every fixture. **16 additional original registrar traces** recover actual selected tables and stop before the initializer callback. [Readable enclosing C](../../components/audio/uart_power_composition_offline/power.c), [pseudocode](pseudocode.md), [successor evidence index and correction](INDEX.md).

Two new enclosing source bodies are deliberately limited to UART domains11..14 and byte-wrapped equivalents. Descriptor/group/callback helpers and PCM2.0 postpone/pending/temperature bodies reuse sealed sources unchanged. PCM2.0 group-control0x5A0786 still executes original instructions in native compositions: action3 is a proven no-op branch. This retained original dependency prevents calling the ELF a complete source-only provider. Delays/status evolution are explicitly synthetic, not physical power or wall-time evidence.

## What the enclosing paths establish

Enable skips all callbacks and status polling when its individual enable bit is already set. Otherwise it invokes pre and action3/enable1 group callbacks, sets the individual bit under saved PRIMASK, restores PRIMASK, invokes post, then waits for the entire shared1E00 status mask to equal1E00. Timeout4 leaves the enable bit set: this body does not roll back the command. Its final status reread returns1 only if the masked group is zero, otherwise0.

Disable skips work if the selected bit is already clear. It invokes pre, clears the bit under saved/restored PRIMASK and checks other enabled devices through the group predicate. If a sibling remains, it skips status poll and group callback, invokes post and returns0 even when shared status remains1E00. If the last device is cleared, it waits for masked status to become **different from1E00**, not necessarily zero. A partial fixture200 therefore passes immediately. Timeout4 leaves the enable bit cleared and still invokes post. Callback return values are ignored here.

Thus success can mean an already-commanded state, sibling sharing, or partial group-status transition. It is not a per-UART power acknowledgement, physical shutdown guarantee or safe quiescence proof. The actual MMIO write is under PRIMASK1; polls and callbacks run after restoring the incoming mask. Incoming1 stays1, incoming0 returns0. No delivered exception/preemption is modeled.

PCM2.0 pre0x5A07E6 sets postponed-publication flag20074F71. Post0x5A07F0 takes its own saved mask, applies latest pending temperature if flagged, clears pending20074F72, clears postponed flag and restores mask. Pending/cache/buck fixtures include actual native VDDF adjustment and all ordered MMIO accesses; disabled cache gates clear the software pending state without a trim write. Existing source behavior is composed, not newly counted as discovered functions.

## Actual callback targets

Registrar0x480434 clears60Btable20073270 and chooses families from CHIPREV4002000C and cached trim-version200001E8. Original instruction traces prove the following group/pre/post Thumb pointers for supplied fixtures:

| Major / trim version | Group | Pre | Post |
| --- | --- | --- | --- |
|21 /0|0|0|0|
|21 /1|59FD37|0|0|
|21 /2,3;22 /0,1;23 /0|5A0787|5A07E7|5A07F1|
|22 /2;23 /1|5A1739|0|0|
|22 /3|0|0|0|
|23 /2,3;24 /0..3|5A490D|0|0|

These are selection fixtures, not known live hardware values. The authenticated initialized trim-version word isFFFFFFFF (uncached), so choosing PCM2.0 from startup data alone would be wrong. Existing trim getter0x47EF38 reads INFO1 word index244 through0x4D3F3C when uncached, caching0 on failure; existing source-backed INFO/calibration work already explains that dependency. Static enclosing initializer0x47FAE8 calls the getter before registrar0x480434, conditional on its calibration-read branch. This identifies where selection becomes concrete; live chip/trim inputs remain unverified. No need to reimplement the already-recovered registrar/getter.

## Correction preserved in successor index

Complete unchanged instruction/MMIO evidence supersedes the prior UART report's incorrect claim of an extra source-only MIS read or NULL difference: **both stock and source writeIEC, readMIS, and fault on the unmapped NULL fixture**. Prior sealed history remains unchanged; successor index links the authoritative correction.

Completed RX rejected-suffix results remain controlled-pressure behavior only, not hardware loss. Whole-system shutdown, actual NVIC/scheduling, DMA, physical power/status side effects and timing remain outside this batch.

Remaining actionable leads are composition with PCM2.1/2.2 group callback families (using their already-recovered sources and explicit planner/apply dependencies), actual initialized calibration selection under supplied INFO data, channel3 IRQ/drain routing and RX receive/notifier. No global source-exhaustion claim. No Git mutations, commits, production/device/shared-state edits.
