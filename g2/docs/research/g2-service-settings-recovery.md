# G2 settings-service linked-object recovery

Status: authenticated analysis closure; not production-routed. The complete
G2 `2.2.6.10` object retained as
`platform\service\settings\service_settings.c` is bounded, recursively
function-mapped, and reconciled against all direct provider edges. No device or
flash state was changed.

## Result

The physical object is `[0x0046B0EC,0x0046C73C)`: 5,712 bytes, SHA-256
`fa6d6bb48321fb41da57627c3f8fa0ec9c4215e21dfd8bea7421b84f7406e9c0`.
Thirty-one functions account for 5,146 bytes. Nineteen literal-pool and
alignment intervals account for the other 566 bytes. Their concatenated
SHA-256 values are respectively
`094b0f0d32f03eadf7e16ac72e17c55e8cb9bebd8eb50326369643eef5ce66de`
and `37645b571c04a9f68c2c671871f6efe4844aff8de6e87ff3053751c5ead71f7a`.

The retained path directly anchors 13 functions. Eighteen adjacent helpers are
admitted by direct ingress, stored-pointer, source order, retained strings,
prior-G2 order, and behavior. Baseline Ghidra omitted eleven executable bodies:

- the battery callback at `[0x0046B3E4,0x0046B44C)`;
- display-apply and settings-send helpers at `0x0046B912` and `0x0046B930`;
- version update, sync dispatch, and service initialization at `0x0046BAEC`,
  `0x0046BBB4`, and `0x0046BE10`;
- the brightness setter and three auto-brightness helpers at `0x0046BFF4`,
  `0x0046C158`, `0x0046C18C`, and `0x0046C1C8`;
- head-up configuration at `[0x0046C524,0x0046C5F2)`.

Each recovered terminal return is byte-pinned. The battery callback also has
the sole stored object entry, Thumb pointer `0x0046B3E5` at `0x0046C698`.
Whole-image ingress is closed at 117 direct entry sites, 94 external entries,
340 in-image body calls, 23 internal body calls, and one stored pointer. There
is no strict-interior BL decode and no direct target in the physical interval
without a mapped entry.

Two halfword scans beginning at `0x0046C44A` and `0x0046C4A0` superficially
decode out-of-image BL targets. They are proven artifacts inside the valid
four-byte `udiv r7,r1,r0` and `mul r0,r0,r4` instructions at `0x0046C448`
and `0x0046C49E`; neither is a provider edge.

The preceding SystemClose UI-lifecycle body at `[0x0046AEEA,0x0046B004)` and
its 232-byte terminal pool are independently pinned. Earlier analysis had
mistakenly included this 282-byte function in the pool; the complete
`systemClose.c` audit now owns it as code. The next object begins at
`0x0046C73C` with an independently rooted LVGL display-buffer synchronization
function. Those boundaries keep both neighbors outside this closure.

The authoritative 31-row inventory, individual body hashes, ingress notes, and
naming confidence are in
`tools/manifests/g2-service-settings-function-map.tsv`.

## Recovered behavior

The service owns product settings policy rather than a reusable upstream
algorithm. Its closed behavior includes:

- OTA, wear, case, silent-mode, display-controller, and app-launch gates;
- a 28-byte settings record whose CRC-16 covers its first 24 bytes;
- peer service identifier 9, version-only command 2, version-request command
  3, local version `2.2.6.10`, and a 500-tick request throttle;
- master/slave settings synchronization, CRC suppression, terminal-mode
  reconciliation, and peer-version tracking;
- settings, ALS Q10 scale, and terminal-mode persistence through three already
  closed KV translation units;
- brightness clamping to 2 through 100, a 13-entry level table, an 11-entry
  luminance ratio table, and role-specific left/right calibration;
- auto-brightness open/close through sensor-hub channel 4;
- head-up enable/disable and angle clamping from -90 through +90 degrees;
- SOC/charging callback handling for contexts zero and one followed by a device
  status notification.

The current function strings preserve the public service names for the main
gates, version synchronization, persistence, brightness conversion, and head-
up control. Descriptive labels are deliberately used for small getters,
setters, and dispatch helpers whose names do not survive in this image.

## Third-party provider resolution

No third-party definition is embedded in the object. Its upstream relationships
end at three previously established seams:

| Provider seam | Calls | Origin/version | Commit boundary | Result |
|---|---:|---|---|---|
| diagnostics | 250 | armink EasyLogger 2.2.99 source-equivalent core plus G2 adapters | `cd93d9c768415f4b7279f2d3ef2366ce15ea087c..a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` | source-admitted core; no settings logic |
| memory/string primitives | 13 | proprietary IAR DLIB/compiler runtime | practical EWARM 9.20+ floor; 9.60.2 remains the leading archive candidate | exact release, Normal/Full option, and archive identity still unobservable; all called bodies are bounded or source-recreated |
| tick getter | 1 | ARM CMSIS-FreeRTOS v10.5.1 plus CMSIS_5 5.9.0 | `d213f261b5be6bb29a7cce8b84071706b72f4d53`; `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` | exact source-owned `osKernelGetTickCount` wrapper |

The remaining 53 provider calls are first-party G2 seams; the complete
non-logging external count is 67 after including IAR and CMSIS. They terminate
at already bounded message transport, display,
sensor-hub, role/case, battery, CRC, and KV objects. In particular:

- the checksum target is the production source-owned first-party
  CRC-16/CCITT-FALSE leaf at `0x0049ACD4`;
- settings, ALS, and terminal writes terminate at the previously closed
  `SVC_KvdbWriteSetting`, `SVC_KvdbWriteAlsScale`, and
  `SVC_KvdbWriteTerminalMode` objects;
- no Cordio, TinyFrame, TLSF, nanopb, LVGL, or other third-party body is linked
  into this object.

This object supplies no new IAR release discriminator. It confirms use of the
same `memcpy`, aligned-copy, `memset`, and `strncpy` entries already included
in the G2 DLIB census, so the honest provenance remains family-level rather
than an invented exact version or commit. The executable provider accounting
is in `tools/manifests/g2-service-settings-provider-map.tsv`.

## Cross-version shortcut and limits

The prior G2 corpus contributes a 21-name ordered settings sequence and
corroborates the long-lived gate, callback, dump, persistence, auto-brightness,
luminance, and table-helper roles. The current object is larger: it adds the
version-sync, ALS-scale, head-up, and terminal-mode paths described above. The
prior corpus is therefore a naming/topology oracle only. Every current body,
pool, return, path pointer, entry, stored pointer, provider edge, and adjacent
boundary is independently authenticated.

The exact Even source revision and private producing commit remain unavailable.
Neither the exact CMSIS/EasyLogger provider commits nor the unresolved IAR
archive identity can identify that first-party revision. Production admission
would require a clean-room service implementation, exact callback/message ABI,
atomic overlay routing, and target hardware validation.

## Reproduce

```sh
make service-settings-closure
```

This runs the fail-closed object/provider analyzer, focused unit tests, and the
aggregate retained-path frontier reconciliation.
