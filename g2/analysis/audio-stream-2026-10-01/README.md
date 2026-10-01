# Source-0 PCM fallback and the 205-byte audio stream body

Bounded recovery completed 2026-10-01. The selected gap was not another audio
symbol inventory: existing references named PCM registration/LC3 functions but
did not give an executable account of packet layout, callback replacement,
encoder failure, or OTA suppression. This batch connects those behaviors.

**Normal body: five 40-byte LC3 frames + two 16-bit algorithm results + one
wrapping sequence byte = 205 bytes.** These are bytes passed to the streaming
transport, not a complete BLE packet. Encoder errors still reach this transport
with a 205-byte body; length alone does not establish valid audio.

## Artifacts and evidence

- [pcm_stream.pseudocode.c](pcm_stream.pseudocode.c): manual readable recovery,
  explicitly separating stock control flow from external algorithm/codec work.
- [audio_stream.h](audio_stream.h): conservative host view of the normal body,
  exact-length check and modular sequence-distance helper. This is not a decoder.
- [verify.py](verify.py), [validation.json](validation.json),
  [disassembly.txt](disassembly.txt): **26 passing stock-instruction scenarios**,
  16 authenticated function bodies, configuration provenance and call traces.

Locked input: `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Thumb/M-class runtime addresses = file offsets + `0x00437FE0`.

The actual audio configuration is in compressed SSRAM initialization data.
The verifier freshly executes stock initializer `0x0043A11E` using descriptor
`0x0075D404`; its 769,646-byte output at `0x20080000` has SHA-256
`a5be949c41cf1e9a7d4a6b4aa6e3a6cb2f9c9bcb3a04a866d15e49e3976a7d0c`.
No ignored decoded file is required to run the verifier. At `0x20108948`, the
seven words are `0, 10000, 16000, 1, 0, 32000, 0`:

| Offset | Recovered meaning | Initial value |
|---:|---|---:|
| +0 byte | PCM format selector | 0, two bytes/sample |
| +4 | LC3 frame-duration argument | 10000 |
| +8 | sample-rate argument | 16000 |
| +12 | channel count / stride | 1 |
| +16 | selected interleaved channel | 0 |
| +20 | bitrate argument | 32000 |
| +24 | cached encoder pointer | 0 |
| +28 | encoder workspace begins | not reconstructed here |

Original LC3 geometry helpers resolve these values to **160 samples and 40
encoded bytes per frame**. At 16 kHz this is 10 ms/frame, consistent with the
duration argument in microseconds. Five frames represent 50 ms of mono audio;
this duration is derived from sample geometry, not a measured delivery cadence.

## Call chain and packet layout

`AUD_CodecDmaInt` (`0x0053C6F2`) compares the current kernel tick with timestamp
at message+8. Age **40 ticks is accepted; 41 is rejected**, verified on original
instructions. Accepted work fetches the current I2S buffer and invokes
`SVC_PcmAppProcessData(0, buffer, bytes)` at `0x0057ADF8`. No millisecond conversion
or real DMA/radio latency is inferred from this test.

With no matching registered source-0 callback, that function runs the algorithm
provider, obtains its front buffer, calls `SVC_Lc3EncodeMono` (`0x0057A940`),
appends metadata, writes the sequence byte, and sends the body. The front-buffer
accessor `0x005915DC` returns a **fixed 1600-byte** mono working buffer. Under the
stock two-byte, single-channel configuration that is 800 samples/five frames.

| Body offset | Normal successful encoding |
|---:|---|
| 0–39 | LC3 frame 0 |
| 40–79 | LC3 frame 1 |
| 80–119 | LC3 frame 2 |
| 120–159 | LC3 frame 3 |
| 160–199 | LC3 frame 4 |
| 200–201 | first algorithm result, little-endian u16 |
| 202–203 | second algorithm result, little-endian; stock diagnostics sign-extend it |
| 204 | previous value of a wrapping u8 counter at `0x2007500E` |

Existing symbols describe the algorithm results as SSR and angle/TDOA, but this
batch does not establish their physical meaning, units, calibration or valid
range. The host header therefore calls them `metadata0` and `metadata1`.

The test algorithm provider writes values `0x1234` and -123, while the codec
stub writes a distinct repeated byte to each frame. Original assembly produces
five correctly placed 40-byte regions and trailer `34 12 85 FF sequence`.
Those repeated bytes are **test markers, not valid LC3 bitstreams**.

`Thread_MsgStreamingNotifyByBle` (`0x00475D78`) checks OTA-transfer activity.
If inactive it calls `Thread_MsgTxByBle(1,1,0,0,body,205,...)`. The common queue,
fragmentation/envelope and BLE characteristic are beyond this batch's boundary.
Do not search an arbitrary BLE notification for an unframed 205-byte pattern
and assume it is this body without resolving that outer transport.

## Callback lifecycle and encoder rules

Two 12-byte source slots begin at `0x20073C20`: app ID u32 +0, source byte +4,
callback pointer +8. `SVC_PcmAppRegister` (`0x0057AB78`) accepts source 0 or 1
and a nonnull callback. **A new registration replaces the previous owner**;
it is not an exclusive-acquire API. `SVC_PcmAppUnregister` (`0x0057ACD0`) clears
an occupied slot only for the matching app ID and leaves it intact on mismatch.
An empty slot returns success. Its body lacks registration's source<2 check;
callers must constrain the source index. No exploitability claim is made.

If a matching callback exists, processing calls it directly with source,
original PCM pointer and byte count, then returns. It bypasses the default
algorithm/LC3/stream path. Source 1 with no callback does nothing in this
function. This matters for CFW microphone consumers: installing a callback can
silence the default streaming path unless the new consumer deliberately forwards
or replaces that work. Callback buffer lifetime beyond this synchronous call
is not proven here.

The encoder wrapper maps format 0→2, 1→4, 2→3, 3→4 bytes/sample; other selectors
fail. It calculates input-frame bytes as sample-width × channels × frame-samples.
Input must divide exactly into that size. Interleaved selection offsets the PCM
pointer by sample-width × selected-channel and passes channel count as stride.
Original-code tests cover mono and two-channel selection over five frames.

An unaligned input returns -1 before resetting the caller's output-length value.
Zero input with otherwise valid geometry succeeds with zero output. Encoder
failure returns -1 and preserves the count of already completed frames. The
API has no output-capacity argument; safe use depends on valid geometry and a
sufficient output allocation. Arbitrary mutable/invalid configurations are not
certified by these tests.

## Failure behavior relevant to SybilSight

The fallback caller initializes encoded length to zero but **ignores the
encoder return code**. It appends metadata at the accumulated encoded length,
then still sends 205 bytes:

| Synthetic codec outcome | Metadata offset | Remaining body before byte 204 |
|---|---:|---|
| All five frames succeed | 200 | none after four-byte metadata |
| First frame fails | 0 | zero-filled bytes 4–203 |
| Second frame fails | 40 | zero-filled bytes 44–203 |

The sequence remains at byte 204 in every case. The failure cases are original
caller/encoder-wrapper behavior with an injected codec failure; they are not
evidence of real codec failures on the device. A receiver must not infer audio
validity from body length or counter advancement. The host view helper exposes
the normal layout; it cannot detect these failures without validating the codec
data or additional context.

OTA suppression occurs **after** processing, encoding and counter advancement.
The original wrapper omits the transport enqueue while the counter still moves.
Counter wrap 255→0 is verified. Thus a gap is useful evidence of missing stream
bodies, but does not uniquely identify radio loss; firmware suppression can also
produce gaps. No connection-specific counter reset was established.

## Validation, limits and next useful target

```sh
~/.local/share/opencfw/venv/bin/python g2/analysis/audio-stream-2026-10-01/verify.py
```

Result: `PASS 26 cases; 16 body hashes`. Native Unicorn execution completed
before SybilSight's quiet baseline. Subsequent work was light artifact writing;
no new heavy analysis/build/UI work was started during the requested hold through
00:34 UTC. The C pseudocode/header were manually reviewed but not compiled in
that window. They are supporting interpretations, not tested firmware source.

Capstone/Unicorn operate on authenticated original bytes. The codec's actual
bitstream encoder, microphone DSP, I2S hardware acquisition, clock and transport
enqueue are explicit stubs. Original frame geometry, channel stepping, callback
routing, packet assembly, OTA gate and DMA-age checks execute normally. Logging
is disabled. No audio quality, bitstream fidelity, physical metadata units,
microphone hardware behavior, BLE delivery, or complete lifecycle is claimed.

The next bounded app-facing target is the common transport's framing and copy
boundary for `(transport=1, subtype=1)` so this 205-byte body can be located and
decoded reliably in host captures. Separately, the algorithm provider can resolve
metadata meaning; neither requires reopening the ring shutdown model.


Verification follow-up after the quiet window release: host C11 syntax checking
with `clang -Wall -Wextra -Werror` passed for this batch’s pseudocode.
The original-instruction receipt above remains the existing26-case result.
