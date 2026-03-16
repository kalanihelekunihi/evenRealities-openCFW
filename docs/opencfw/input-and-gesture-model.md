# Input and Gesture Model

This document is the clean-room model for temple touch, gesture transport, wear-gated input policy, and ring gesture integration across the G2 runtime.

## Input Matrix

| Domain | State | Main Evidence | Identified Constraints | Remaining Gaps |
|---|---|---|---|---|
| Touch-controller boundary | Identified | touch bundle RE, topology docs, device notes | CY8C4046FNI is a separate I2C-attached controller with its own DFU path and gesture/proximity growth across versions | exact runtime event grammar, thresholds, and calibration tables |
| Dual gesture event planes | Identified with bounded unknowns | gesture docs, NUS notes, firmware RE | tap/swipe and long-press behavior surface on protobuf lanes and on NUS `0xF5`; both planes are implementation-relevant | exact arbitration and dedupe policy when both planes report one physical action |
| Wear-gated input policy | Identified with bounded unknowns | wear-detection module, settings strings, firmware RE | wear enable/status are real and can block input and display-adjacent control | exact selector wire contract and edge transitions |
| Gesture customization and screen-state policy | Partial | firmware RE, universal-setting strings, gesture docs | per-gesture screen-on and screen-off mappings exist as runtime policy, not hardcoded action bindings | exact wire schema, persistence layout, and app-type enum map |
| Ring gesture bridge | Partial | ring docs, ring-relay module, gesture docs | ring gestures feed into the same user-input domain through a separate relay path | exact direct versus phone-mediated routing and `RING_CmdTouchUpdata` decode |
| Long-press and release metadata | Partial | gesture docs, NUS release code, firmware RE | long press carries nested metadata on `0x0D-01` and NUS has an explicit release code | exact long-press counter semantics and release correlation |

## Identified Input Contracts

### CY8C4046FNI Remains a Separate Input Boundary

- The touch controller is a distinct PSoC4 firmware target updated over I2C DFU from Apollo510b.
- Gesture recognition and proximity-related behavior are not just raw Apollo GPIO work.
- The large firmware growth at v2.0.6.14, including proximity baseline capture and fast-click reset strings, makes the touch boundary important enough to preserve explicitly in `openCFW`.

### Gesture Events Arrive on More Than One Plane

- G2-layer gesture events arrive on the control notify plane:
  - `0x01-01` for tap and swipe families
  - `0x0D-01` for long-press and adjacent compact-notify behavior
- NUS delivers gesture bytes under the `0xF5` prefix with explicit codes for tap, double tap, triple tap, long press, release, and slide directions.
- Clean-room implication: `openCFW` should normalize gesture meaning above transport rather than pretending one wire format is the only truth.

### Wear State Gates Input and Some Display Control

- Wear detection has explicit enable and status state.
- Firmware strings show that when wear-detect input is not enabled, input events are blocked and some display-adjacent control paths are also refused.
- Clean-room implication: wear status should sit in front of input routing and display activation policy rather than being treated as a cosmetic status flag.

### Gesture Policy Is Configurable

- Firmware evidence closes a real gesture policy layer with independent mappings for:
  - screen on
  - screen off
- That means gesture decoding and gesture-to-action policy should remain separate layers in `openCFW`.

### Ring Gestures Share the User-Input Surface, Not the Same Transport

- Ring gestures are real first-class input sources.
- Current evidence shows gesture translation into G2-facing actions through NUS-like tap/swipe/hold codes and through the `0x91` relay family.
- Clean-room implication: ring gestures should join the same logical input domain, but only through a dedicated adapter rather than being merged into touch-controller code.

## Inferred Input Behavior

### Dual Gesture Planes Likely Serve Different Latency or Compatibility Roles

- The protobuf gesture plane and the NUS `0xF5` plane likely coexist for latency, compatibility, or feature-specific routing reasons.
- That is strong enough to keep both planes in the architecture, but not strong enough to freeze exact producer precedence yet.

### Long-Press Metadata Is More Than a Boolean

- The recovered nested counter on `0x0D-01` strongly suggests long press carries duration, zone, dedupe, or sequence metadata rather than a simple pressed flag.
- `openCFW` should therefore keep long-press metadata structured and instrumented.

### Ring Gesture Routing May Be Topology-Dependent

- Local evidence supports both phone-mediated translation and more direct ring-to-glasses interaction.
- The exact path likely depends on connection topology and which endpoint currently owns ring state.

### Wear Gating Probably Affects More Than Touch

- Current evidence already closes wear-based gating for input and display-adjacent control.
- It is likely that feature activation and some proactive notifications are also influenced by wear state, but that broader policy split is not fully closed.

## Unidentified Areas

- Exact long-press counter semantics on `0x0D-01`.
- Exact arbitration or dedupe rules between protobuf gesture events and NUS `0xF5` gesture events.
- Exact screen-on/screen-off gesture policy schema, persistence layout, and app-type enum mapping.
- Exact touch-controller runtime event grammar, debounce thresholds, and calibration tables beyond the DFU boundary.
- Exact `RING_CmdTouchUpdata` tick/type mapping and how it lands in the user-visible gesture model.
- Exact boundary between wear gating, touch input acceptance, and feature-level gesture policy.

## Clean-Room Rules

- Keep touch-controller transport and DFU separate from gesture-policy code.
- Preserve both gesture event planes instead of forcing all input through one guessed transport.
- Put wear gating in front of input dispatch and display-adjacent control.
- Keep gesture decoding separate from gesture-to-action policy.
- Treat ring gestures as adapters into the shared input model, not as raw touchbar aliases.

## Source Documents

- `../features/gestures.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/modules/wear-detection.md`
- `../firmware/modules/ring-relay.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/g2-firmware-modules.md`
- `../devices/g2-glasses.md`
- `../devices/r1-ring.md`
- `../protocols/nus-protocol.md`
