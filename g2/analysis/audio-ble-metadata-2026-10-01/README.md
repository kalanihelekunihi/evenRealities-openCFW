# Audio over ESS: framing, queue behavior and metadata meaning

Completed 2026-10-01; extends the [205-byte body recovery](../audio-stream-2026-10-01/README.md).
This batch follows the actual transport=1 path, rather than applying the generic
multipart transport description to every profile.

**The normal audio value is sent directly as an ESS notification on handle
`0x0864` in this locked build.** Its raw ATT PDU is `1B 64 08` followed by the
205-byte body. There is no `0xAA` multipart envelope, added CRC or extra sequence
field on this path. Metadata is an integer energy ratio and signed degrees,
with important validity limitations below.

## Artifacts and provenance

- [ess_metadata.pseudocode.c](ess_metadata.pseudocode.c): reconstructed queue,
  ESS ownership, preprocessing, ratio and angle conversion behavior.
- [ess_audio.h](ess_audio.h): parsers for a native 205-byte GATT value and a
  reassembled 208-byte raw ATT PDU. Structural acceptance does not certify audio.
- [verify.py](verify.py), [validation.json](validation.json),
  [disassembly.txt](disassembly.txt): **30 passing original-instruction cases**,
  13 authenticated bodies, call traces, raw ATT vectors and metadata results.
- [test_header.c](test_header.c): host parser assertions supplied for reproduction.

Input remains `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Thumb addresses = file offset + `0x00437FE0`. The verifier checks the full image
and body hashes before running. Runtime queue/connection state is synthetic and
explicit. No firmware patch, flashing, commits or shared campaign edits.

## Exact audio path and copy boundaries

1. The previous batch's `Thread_MsgStreamingNotifyByBle` supplies transport=1.
2. `Thread_MsgTxByBle`, `0x0047564E`, allocates `(length+14)&~3` bytes from the
   file heap and **copies** the body into a queue record. At length 205 this is
   a 216-byte allocation containing u32 type=2 at +0, u32 length=205 at +4,
   then the 205 bytes at +8. The internal header/padding are not transmitted.
3. `threadBleMsgTxQueueDrain`, `0x0047538C`, selects type 2, takes a TX token
   with argument 50 (tick-related timeout), then calls `APP_BleEssSendDataMsg`
   at `0x004BE2F6`. Unlike queue types 1/4/8, type 2 does not call a multipart
   encoder. The queue record is freed after this call, or on token failure.
4. ESS requires a nonzero connection, CCC-enabled byte equal to 1, and no active
   OTA transfer. It queues a 12-byte WSF event `0xA9` containing the body pointer
   and length. **This second handoff borrows the pointer.**
5. `essProcMsg`, `0x004BE24E`, handles `0xA9` by calling
   `AttsHandleValueNtf(conn,0x0864,length,pointer)` at `0x00533ED8`.
6. `attsHandleValueIndNtf`, `0x00533C6C`, validates the connection/client state
   and MTU, then allocates and copies the payload into an ATT-owned packet.
   The opcode is `0x1B`, followed by the little-endian handle and unchanged body.

Original queue, drain, ESS handler and ATT construction instructions execute in
the harness. The test overwrites the original caller buffer after enqueue and
confirms the first heap copy preserves the body. The test ATT PDU is exactly
`1B 64 08`, 200 bytes of marker `55`, and trailer `12 00 D3 FF 07`.
These are synthetic codec markers, not valid LC3 data or a captured notification.

The decompiler's queue-drain export had incorrectly removed most branches as
unreachable. This batch recovers the type-2 path from the 302-byte original body
and exercises it; it does not rely on that misleading decompiler output.

### A bounded ownership caveat

The queue record can be freed before a later WSF callback performs ATT's copy.
A synthetic delayed-consumer test poisons the freed file-heap record and shows
that ATT copies the poison bytes. This establishes the local borrowed-pointer
dependence, **not a hardware use-after-free occurrence**. Task preemption may
allow WSF to copy first; allocator reuse and actual scheduling were not measured.
Do not claim the first enqueue copy alone makes the entire path independently
owned. This batch documents the dependency and does not implement a patch.

## Delivery gates and limits

The TX CMSIS queue has **150 pointer entries**, confirmed by executing its
constructor. For transport 1, `count >= capacity/2` frees the newly copied record
and returns zero. Tests prove enqueue at 74 and drop at 75/149. Thus apparent
API success does not mean delivery.

The misleadingly named `ble_msgtx_isConnected` reads whether connection-parameter
mode is fast event `0xA3`. When false, the producer requests fast mode but still
enqueues. ESS separately performs its connection/CCC checks. Tests also cover
missing queue, allocation failure, queue-put failure, token timeout, explicit
queue clear, disabled CCC, disconnected ESS, OTA and WSF-allocation failure.

An unchanged 205-byte notification requires **ATT MTU >= 208**. Original ATT
code accepts MTU 208/247 and rejects 207 with callback status `0x77`.
No fragmentation into smaller ATT notifications occurs in this path. Normal
lower-layer BLE/L2CAP segmentation remains separate and was not emulated.

The handle `0x0864` is exact for this firmware artifact, not a stable UUID or
cross-version contract. This batch does not recover the ESS service/characteristic
UUIDs. Use the app's discovered characteristic mapping or a known-good capture
to bind this handle; do not invent a UUID or reuse the ring service UUID.

## Metadata0: dimensionless integer energy ratio

`algo_front_data_preprocess`, `0x005915EA`, separates 800 interleaved signed
16-bit stereo pairs. It computes mean-square energy for each channel and a mono
buffer using `left/2 + right/2` with integer truncation. The normal input is
3200 readable bytes; although its initial check accepts some shorter lengths,
the loop still reads 800 pairs. The tests use the full normal buffer.

`service_algo_energy_window_update`, `0x00591C26`, writes a PCM mean-square value
into a ten-entry circular u64 window. Its index wraps modulo ten. The precise
time cadence/source of window updates is not traced here.

`SVC_SSRProcess`, `0x0059173A`, returns zero if either current channel energy is
zero. Otherwise its observed normal arithmetic is:

```text
current  = floor((left_mean_square + right_mean_square) / 2)
baseline = floor(sum(window[0..9]) / 10)
metadata0 = low_u16(floor((current + 1) / (baseline + 1)))
```

This is **not dB**, a calibrated loudness value, or a probability. There is no
logarithm or saturating clamp. The low 16 bits are retained: a synthetic ratio
65,537 yields 1. The `+1` terms avoid a zero denominator in normal arithmetic.
No claim is made for overflowing pathological u64 state.

Tests cover unity, a ratio of 18, a zero channel and u16 truncation. A further
test executes preprocessing on constant channels 10 and 30: their mean squares
are 100 and 900, mono samples are 20, and a baseline of 100 produces ratio 4.
A window update with samples +3/-3 stores 9 and advances the index.

The original ratio/preprocessing instructions run; the compiler's 64-bit division
helper is an explicit mathematical quotient/remainder stub. Its corpus boundary
is oversized and rejected, so this batch does not misrepresent that whole region
as newly verified code.

## Metadata1: signed integer degrees

`service_algo_source_angle`, `0x00591BA4`, requests cross-correlation over 800
samples and lag limit 10, then executes:

```text
metadata1 = int16(truncate_toward_zero(angle_radians * 180.0 / pi))
```

The literal doubles are exactly 180 and the stored approximation of pi at
`0x00591CF8` and `0x00591D0C`. Tests execute the original multiply/divide/VFP
conversion with correlation supplying controlled radians: 0→0, ±pi/2→±90,
and ±0.5→±28. The default Unicorn M-class model rejects these double-precision
instructions; these five tests use its Thumb/VFP mode instead, with that change
explicit in the verifier. They verify instruction conversion semantics, not a
complete Apollo CPU or real acoustic estimator.

The field's **numeric unit is degrees**, but physical orientation, channel sign,
calibration, confidence thresholds, unavailable-angle/NaN behavior and the actual
correlation algorithm remain unverified. Do not equate zero with a confirmed
straight-ahead source or label positive values as left/right without evidence.

## Direct app interoperability guidance

- At a native GATT notification callback, parse the **205-byte value directly**.
  At a reassembled raw ATT capture, require `1B 64 08` plus those 205 bytes.
  HCI/L2CAP framing must be removed separately. No extra application length
  field is present; the notification boundary supplies the length.
- Negotiate/verify MTU >=208 and enable the correct ESS notifications before
  expecting complete normal values. The CCC state adapter uses index 3; that
  index is internal firmware configuration, not an on-wire descriptor handle.
- On normal successful encoding, split bytes 0–199 into five 40-byte LC3 frames
  configured for 16 kHz mono, 10 ms, 32 kb/s. Read energy ratio LE16 at 200,
  signed degrees LE16 at 202, and sequence byte at 204.
- Treat sequence distance modulo 256 as a discontinuity hint. OTA suppression,
  half-full queue drops, token failure, queue clearing or ATT rejection can
  cause gaps; radio loss is not the only explanation. Multiple wraps and
  reordering cannot be resolved by this byte alone.
- **There is no explicit encoder-success flag in the recovered body.** The
  previous batch proves that codec failures still send 205 bytes while placing
  metadata after only the frames completed. Parsing length/trailer cannot
  positively distinguish failure. Decoder errors or suspicious content can
  support an inference, but even a decodable payload does not certify the
  firmware's intended sample/metadata provenance.

The helpers deliberately provide structural parsing, not an `audio_valid`
predicate. Application-side diagnostics should keep malformed notifications,
sequence gaps and LC3 decode outcomes separate rather than report a single
definitive cause.

## Reproduction and stopping boundary

```sh
~/.local/share/opencfw/venv/bin/python g2/analysis/audio-ble-metadata-2026-10-01/verify.py
clang -std=c11 -Wall -Wextra -Werror -fsyntax-only g2/analysis/audio-ble-metadata-2026-10-01/ess_metadata.pseudocode.c
clang -std=c11 -Wall -Wextra -Werror g2/analysis/audio-ble-metadata-2026-10-01/test_header.c -o /tmp/opencfw-ess-header-test
/tmp/opencfw-ess-header-test
```

The native verifier passed before the second SybilSight quiet window. The new
C helper/pseudocode and host assertions were written and manually reviewed during
that hold; the host compile/test commands were not run. No heavy job was started
after readiness was reported at approximately 00:40 UTC; the seven-minute hold
remains applicable unless released by the parent task.

Providers stubbed in these tests include allocator backing, RTOS queues/flags,
TX token, connection/CCC/OTA state, ATT client awareness, integer division and
correlation. Actual queue/ESS/ATT constructors and metadata instructions execute;
no radio, acoustic input or live scheduling is emulated. This is not firmware
source completeness, hardware fault confirmation, or byte-identical rebuilding.

Remaining app-specific inputs are the discovered ESS characteristic mapping,
negotiated MTU and actual received notifications. Physical angle interpretation
requires known source/channel orientation or calibrated input evidence. Those
facts are not filled in by assumptions. A further static GATT-table recovery
could supply UUIDs; actual delivery timing requires a faithful model or capture.


Verification follow-up after the quiet window release: host C11 syntax checking
with `clang -Wall -Wextra -Werror` passed for this batch’s pseudocode.
The ESS parser assertion executable also passed; original-instruction verifier
rerun passed all30 cases and13 body hashes.
