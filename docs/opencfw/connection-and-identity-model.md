# Connection and Identity Model

This document is the clean-room model for the G2 BLE identity, authentication, connection, and endpoint-routing plane across the left eye, right eye, and ring-adjacent profiles.

## Connectivity Matrix

| Domain | State | Main Evidence | Identified Constraints | Remaining Gaps |
|---|---|---|---|---|
| BLE identity and endpoint split | Identified with bounded unknowns | device docs, firmware RE, BLE multi-connection notes | left and right run the same firmware but expose runtime-selected identities; both maintain independent phone BLE links; ring remains a separate profile boundary | exact advertising-set policy and fallback behavior |
| App-layer auth family | Identified | auth protocol notes, transport docs, firmware RE | auth uses the `0x80` family and ends in time sync; normal session establishment does not depend on BLE pairing | exact failure codes and retry policy |
| Per-connection routing and sequence state | Identified with bounded unknowns | captures, BLE multi-connection notes, device docs | responses, keepalives, and non-auth sequence counters are endpoint-local compatibility surfaces | full routing closure for every async producer path |
| Auth keepalive and heartbeat safety | Partial but executable | auth docs, firmware RE | `0x80-01` periodic status exists, `0x80-02` is a transport ACK, and unsafe heartbeat types are documented | full field map and disconnect-escalation semantics |
| Advertising and discoverability | Partial | firmware string evidence, device docs, firmware RE | advertising control exists, normal-runtime and DFU identities are distinct, and multiple endpoint identities are implementation-relevant | exact restart, fallback, and ring-discovery policy |
| Ring identity boundary | Partial | ring docs, BLE multi-connection notes, firmware RE | ring traffic is a separate BLE/runtime profile from G2 and NUS traffic | exact `connectRing` ownership and discovery path |

## Identified Connectivity Contracts

### Identity Is Runtime-Selected, Not Build-Selected

- Left and right eyes run the same main firmware image.
- Runtime identity is selected by role and advertising identity rather than by separate left/right builds.
- Both eyes maintain independent BLE connections to the phone and each eye keeps its own sequence evolution.
- Ring-facing traffic is a separate identity and profile boundary and should not be merged into the normal G2 endpoint contract.

### Authentication Is a Dedicated Application-Level Family

- Auth uses `0x80-00`, `0x80-20`, `0x80-01`, and `0x80-02`.
- Two handshake families are strongly anchored:
  - fast 3-packet auth
  - full 7-packet auth
- Both flows end with a time-sync packet and both are application-layer compatibility behavior rather than BLE-pairing behavior.
- `0x80-01` auth success uses glasses-generated message IDs rather than echoing the sender's auth message ID.
- `0x80-02` is a transport ACK with header-only behavior.

### Dual-Eye Compatibility Requires Endpoint-Local Context

- Left and right eyes respond independently even during the same session.
- Current evidence is strong enough to preserve these implementation rules:
  - keep per-endpoint sequence counters
  - keep notify routing endpoint-local
  - keep auth keepalive scheduling endpoint-local
  - keep deferred async emissions bound to the originating connection context
- Clean-room implication: `openCFW` should not treat dual-eye state as one global BLE session.

### Sequential Dual-Eye Auth Is the Safe Compatibility Baseline

- Current app and capture evidence shows dual-eye auth should remain sequential.
- The main compatibility reason is shared response-decoder pressure on the phone side rather than a proven firmware inability to answer concurrently.
- `openCFW` should therefore preserve sequential auth compatibility until stronger live evidence proves concurrent auth is safe.

### Runtime and DFU Identities Must Stay Separate

- Normal runtime advertising uses the G2 identity surface.
- DFU mode advertises as `B210_DFU` and exposes the Nordic Secure DFU family instead of the normal G2 runtime services.
- Clean-room implication: normal runtime, recovery, and DFU identities should stay explicitly separate in code and docs.

## Inferred Connectivity Behavior

### Advertising Restart and Fallback Policy Exists

- Firmware strings and multi-endpoint evidence strongly suggest active advertising control, restart logic, and more than one discoverability mode.
- The exact multi-set versus fallback policy is still not closed strongly enough to freeze as final implementation truth.

### Auth Keepalive Participates in Session Health

- Firmware evidence shows a periodic auth-success or heartbeat cadence on `0x80-01`.
- The safety notes around heartbeat types strongly suggest the keepalive family is tied to session health and can trigger disruptive state changes if used incorrectly.

### Ring Discovery Is Not Just Another G2 Connection

- Ring connect and state control exist, but the exact split between phone-driven ring discovery, glasses-mediated ring actions, and direct ring runtime behavior is still mixed in local evidence.
- `openCFW` should therefore keep ring connection logic behind a separate identity/profile layer rather than treating it as a third glasses endpoint.

### Connection Parameters Likely Shift by Mode

- OTA fast-mode and low-power BLE behavior are both visible in local evidence.
- That strongly suggests connection parameters, advertising policy, or link posture vary by runtime mode even though the final state machine is still incomplete.

## Unidentified Areas

- Exact auth keepalive payload schema, field numbering, and failure escalation rules.
- Exact advertising-set scheduling, watchdog restart, and fallback policy across left/right/ring identities.
- Exact connection-parameter update policy, retry backoff, and OTA fast-mode transitions.
- Exact `connectRing` ownership and whether ring discovery is always glasses-mediated, sometimes direct, or mode-dependent.
- Exact endpoint-local routing closure for every deferred async emitter outside the currently anchored feature families.

## Clean-Room Rules

- Keep the `0x80` auth family separate from ordinary feature-service handlers.
- Preserve endpoint-local sequence, keepalive, and notify-routing context for left and right eye sessions.
- Keep dual-eye auth sequential as the default compatibility posture.
- Keep normal runtime identities separate from DFU identity.
- Keep ring connection/profile handling separate from the G2 and NUS endpoint contract.

## Source Documents

- `../protocols/authentication.md`
- `../protocols/connection-lifecycle.md`
- `../firmware/modules/ble-multi-connection.md`
- `../devices/g2-glasses.md`
- `../devices/r1-ring.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/firmware-communication-topology.md`
