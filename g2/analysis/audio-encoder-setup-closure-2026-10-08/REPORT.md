# LC3 encoder setup and in-place reset

**181 PASS original/independent setup comparisons**, with complete selected setup instructions and actual copy/zero providers, no result stubs. [Independent source](../../components/audio/encoder_setup_offline/setup.c), [helper interface](../../components/audio/encoder_setup_offline/setup.h), [results](results.json), [provenance](provenance.json), [disassembly](original-disassembly.txt).

`0x57A926(config)` calls standard encoder setup `0x591374` with config+4 duration, config+8 sample rate, PCM rate 0 (fallback to codec rate), and **workspace at config+28**. It writes the returned encoder pointer at config+24. Unlike a lazy initialization check, it **always reinitializes a non-NULL config**, including an existing encoder. NULL config does nothing. Invalid selectors replace the stored pointer with NULL; workspace remains untouched in the selected invalid paths. No encoder free or allocation occurs here.

## Selectors and layout

The standard wrapper chooses high-resolution mode 0. Duration helper `0x590D3C` maps 2500/5000/7500/10000 to indices 0/1/2/3. Rate helper `0x590D74` maps 8000/16000/24000/32000/48000 to 0..4 in standard mode; nonzero high-resolution mode accepts 48000/96000 as 5/6 and rejects duration 7500. PCM rate ≤0 falls back to codec rate. Setup rejects unsupported duration/rate, PCM index lower than codec index, or NULL workspace. Duration/rate numeric units are consistent with LC3 microseconds/hertz and stock configuration, rather than inferred scheduler tick units.

| Workspace offset | Recovered value |
| --- | --- |
| +0 / +1 / +2 | duration index / codec rate index / PCM rate index, one byte each |
| +0x4A0 | geometry[PCM index]/2 |
| +0x4A4 | ((duration index+1)×geometry + geometry/2)/2 |
| +0x4A8 | (duration index+1)×geometry + previous offset value |
| +0x4AC onward | zeroed sample/history storage, span below |

Locked table `0x7728D4` is `{20,40,60,80,120,120,240}`. Original builds and zeroes a 0x4B0-byte temporary state, copies it into caller memory, then zeroes history beginning +0x4AC. For supported positive inputs, original signed-multiply reciprocal divisions agree with:

```
ns = floor(pcm_rate * duration / 1,000,000)
nd = floor(pcm_rate * 1250 / 1,000,000)
lookback = floor(pcm_rate * (duration == 7500 ? 2000 : 1250) / 1,000,000)
history_bytes = 4 * (ns + floor((nd + ns)/2) + floor(ns/2) + lookback)
```

This is the setup's **written initialization span**, not proof that later encoding never accesses more memory. The routine accepts no capacity argument. For stock duration 10000, rate 16000: indices `{3,1,1}`, offsets `{20,90,250}`, history 1400 bytes; writes end at workspace+2596. With 28-byte config prefix, the initialization occupies 2624 bytes. Stock diagnostic config spacing is 2628 bytes. Do not use this observed span alone as a generic allocation contract for the encode body.

## Validation scope

178 selector/wrapper fixtures compare return value, config pointer, **the entire 32,768-byte constructed workspace region including unchanged sentinels**, and original memory-provider call arguments. Three further cases use the authenticated diagnostic config words at `0x20106A7C`, `0x201074C0`, `0x20107F04` from the previously sealed whole-startup decoder result. Original and independent reset agree at those actual addresses. The existing decoder result's hash is pinned in results; whole-record decode coverage is inherited, not counted as new here.

Actual original `0x48949C`, `0x439C04`, `0x4D4CCC` and their copy/zero bodies run. Independent C implements selectors/geometry/zeroing with its own stores. No allocator, encoder frame production, mutex, live scheduling, DSP hardware or deinit continuation is modeled. Workspace fixtures are mapped synthetic RAM, not observed device state. Caller ownership and workspace sizing for the complete codec remain separate dependencies.

This closes the LC3 setup entry boundary from diagnostic deinit, and provides a reusable behavioral setup helper. It does not complete file-close, hardware-stop, a full LC3 implementation or firmware reconstruction.
