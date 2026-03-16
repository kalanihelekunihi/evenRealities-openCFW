# Audio and Voice Model

This document is the clean-room model for the Apollo510b audio, microphone, and voice-feature stack across the GX8002B codec, the NUS side channel, peer-eye coordination, and phone-side speech or AI orchestration.

## Audio Matrix

| Domain | State | Main Evidence | Identified Constraints | Remaining Gaps |
|---|---|---|---|---|
| Codec boot and host boundary | Identified | codec bundle RE, topology docs, runtime thread map | Apollo boots GX8002B over TinyFrame using FWPK-wrapped BINH stage1 and stage2 images; codec stays a separate host-managed subsystem | exact steady-state command and event dictionary |
| NUS mic and audio side channel | Identified with bounded unknowns | NUS protocol notes, G2 device docs, firmware RE | microphone enable uses raw NUS bytes; streamed mic frames are not normal G2-envelope packets; gesture traffic shares the same low-latency lane | exact echo, heartbeat, and recovery semantics |
| Audio-owner arbitration and peer sync | Identified with bounded unknowns | `service_audio_manager` strings, topology docs, runtime task notes | only one app or feature can own live microphone capture at a time; audio state is synchronized to the peer eye | exact appId map and forced-handoff ordering |
| Voice-feature integration | Partial | EvenAI and Conversate docs, module summaries | voice-facing features exist above the capture path and should not bypass microphone ownership rules | exact EvenAI command surface, exact Conversate audio lifecycle details |
| Wake-word, VAD, and preprocess split | Partial | codec notes, wakeup-response strings, firmware RE | GX8002B owns LC3-adjacent encode and preprocess work; wake-word and VAD hooks exist before phone-side assistant logic | exact boundary between codec, Apollo runtime, and phone app |
| Phone-side speech and AI orchestration | Identified | firmware RE, G2 device notes, app-facing feature docs | glasses are capture or display endpoints first; decode, denoise, VAD, ASR, transcription, and higher-order assistant logic stay phone-owned | exact offline versus cloud dispatch policy inside the phone stack |
| Right-eye microphone authority | Partial | hardware notes, topology docs, firmware RE | right-eye microphone primacy is repeatedly documented and peer sync exists | final split between right-eye capture ownership and master-role policy decisions |

## Identified Audio Contracts

### GX8002B Is a Separate Runtime Boundary

- Apollo510b loads `firmware_codec.bin` into the GX8002B over TinyFrame using a two-stage BINH boot flow.
- The codec boundary owns LC3-adjacent encode, microphone preprocess, and wake-word or VAD-adjacent work.
- The codec image is byte-identical across recovered G2 firmware versions, which makes the Apollo-side host boundary more important than subordinate-code drift for `openCFW`.

### NUS Is the Low-Latency Microphone Lane

- NUS uses raw bytes without the normal G2 envelope, CRC, or protobuf framing.
- `0x0E 0x01` enables microphone streaming and `0x0E 0x00` disables it.
- Glasses-to-phone `0xF1` notifications carry 10 ms, 40-byte LC3 frames. App-visible code sometimes calls this PCM, but the recovered frame size and codec evidence close that as LC3-compressed transport.
- `0xF5` gesture traffic shares the same side channel, so `openCFW` should preserve NUS as a dedicated low-latency path instead of folding it into the protobuf service router.

### Audio Ownership Is Explicit, Not Implicit

- Firmware strings close a dedicated audio manager that tracks who owns the live PCM or microphone stream.
- When a new feature claims audio, the previous owner is forcibly unregistered.
- Audio state is synchronized to the peer eye with dedicated audio sync messages, which means capture ownership and cross-eye state propagation are part of the runtime contract.

### Speech Intelligence Remains Phone-Side First

- The glasses-side contract is capture, encode, wake-word or preprocess, and display coupling.
- The phone-side contract is LC3 decode, denoise, AGC, VAD, ASR or transcription, and higher-order assistant behavior.
- `openCFW` should therefore begin as a voice-compatible capture and display runtime, not as a speculative on-glasses AI stack.

## Inferred Audio Behavior

### EvenAI and Conversate Share the Same Audio Resource

- EvenAI and Conversate are distinct feature families, but both sit above the same recovered microphone and codec plumbing.
- Conversate explicitly exposes `use_audio`, and firmware strings show microphone ownership takeover behavior, which strongly suggests these features compete for a shared audio resource rather than owning separate capture paths.

### Wake-Word Handling Is Layered

- Local evidence strongly suggests a layered model:
  1. microphone capture and codec-side preprocess
  2. wake-word or VAD gating on-glasses
  3. phone-side decode, transcription, or assistant orchestration
- The exact event payloads and edge ownership are still open, so this should stay instrumented in `openCFW`.

### Right-Eye Audio Primacy Exists, but Policy Is Still Mixed

- The right eye is repeatedly documented as the primary microphone or audio producer.
- The left eye still participates in master-role and display-oriented control, and peer audio sync is real.
- Clean-room implication: keep microphone producer choice configurable until the exact policy split closes further.

### NUS Session Liveness Is Richer Than a Simple Toggle

- NUS heartbeat and mic-control echo behavior likely participate in stream liveness and background-session persistence.
- That is strong enough to preserve a separate session manager in code, but not strong enough to freeze timing or retry rules yet.

## Unidentified Areas

- Exact GX8002B steady-state TinyFrame command and event dictionary after BINH boot.
- Exact NUS microphone enable echo, heartbeat cadence, and stream-recovery behavior.
- Exact appId mapping and forced-unregister ordering in the audio manager.
- Exact wake-word and wakeup-response payload schema and ownership split between codec, Apollo runtime, and phone app.
- Exact canonical boundary between EvenAI, Conversate, and any separate transcribe service or lane.
- Exact fallback rules when right-eye audio capture is unavailable or peer roles change.

## Clean-Room Rules

- Keep codec boot and runtime control in a dedicated host adapter instead of hiding it inside feature services.
- Keep NUS microphone or audio transport separate from the normal `0x5401`, `0x6401`, and `0x7401` protobuf lanes.
- Enforce single-owner microphone arbitration in the runtime architecture even before the full appId map closes.
- Treat phone-side speech and assistant orchestration as the baseline compatibility target.
- Keep wake-word, VAD, and cross-eye audio policy behind instrumentation until field-level closure improves.

## Source Documents

- `../protocols/nus-protocol.md`
- `../devices/g2-glasses.md`
- `../features/even-ai.md`
- `../features/conversate.md`
- `../firmware/codec-gx8002b.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/device-boot-call-trees.md`
