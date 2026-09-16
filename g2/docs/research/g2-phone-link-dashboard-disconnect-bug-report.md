# G2 dashboard shows “phone disconnected” while an existing Bluetooth link blocks another phone

Draft bug report, prepared 2026-09-16. Not submitted externally.

## Summary

An iPhone can hold a Bluetooth connection to the G2 while its control app is not running. In the reported reproduction, the G2 stopped appearing as connectable to an Android phone, but the stock dashboard continued to show the crossed-out phone icon. The wearer therefore had no on-glasses indication of the connection preventing the second phone from connecting.

OpenCFW's recovered stock code supports a concrete explanation for the misleading icon: the dashboard uses an aggregate BLE status that is true only when **both self and peer glasses' BLE status bits are set**. It does not directly ask whether any phone-facing Bluetooth link is occupied. A partial or incompletely synchronized connection can therefore appear identical to no connection.

This is a code-supported explanation, not a confirmed diagnosis of the reported iPhone session. The missing bit, link topology, and reason Android could not connect still require a trace of that reproduction.

## Environment

- Hardware: Even Realities G2; iPhone and Android phone.
- Observed firmware/UI: stock dashboard; firmware version not supplied.
- Phone models, OS versions, app names/versions: not supplied.
- iPhone app condition: reported as not running; force-quit versus background/suspended state not established.
- Code analyzed: OpenCFW checkout at `191a64ae160c984aded35f789fbecc3003928b23`, with existing unrelated working-tree changes. The evidence below concerns the repository's **stock G2 2.2.6.10** reference image and its recovered code. It must not be assumed identical to an unspecified installed firmware version.

## Reproduction reported by the user

1. Have the iPhone connect to the G2 while the iPhone control app is not running.
2. Attempt to discover/connect to the G2 from the Android phone.
3. Inspect the phone-connection indicator in the stock G2 dashboard.

**Actual:** The Android phone cannot connect; the user reports that the G2 is no longer advertising as connectable. The dashboard still displays the crossed-out phone icon. The user reproduced this behavior.

**Expected:** The glasses should visibly distinguish no phone link from an occupied or partial phone link, even if the connected phone never sends a control-app message. App/session readiness may be displayed separately.

**Impact:** The disconnected icon suggests that the glasses are free to connect while another phone is occupying a connection. This makes troubleshooting and switching phones confusing.

## Code findings

### 1. A raw phone-facing connection is recorded independently

The peripheral handler `_bleSlaveProcMsg` at `0x0046E098` handles connection-open event `0x27` and connection-close event `0x28`. On open, `appSlaveConnOpen` at `0x0046DE78` saves the connection ID at controller-context offset `0x54`. On close, the peripheral handler clears that field. Getter `0x0046EFD8` returns it directly.

This provides an existing firmware-side signal for whether the local phone-facing link is occupied, independent of the dashboard's aggregate boolean. The field describes the peripheral connection; it must not be confused with the separate ring connection.

Sources: [peripheral function map](../../tools/manifests/g2-app-ble-peripheral-function-map.tsv), [recovered decompilation](../../research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-02.c) at lines 12538–12551, 12730–12746, 12766–12792, and 13161–13168. The decompilation is analysis material, not compilable vendor source.

### 2. “System BLE connected” requires both glasses' status bits

`UX_GetSystemBLEStatus` at `0x0047D8CE` reads the packed byte at `0x20075043` and returns:

```c
(status & 0x0c) == 0x0c
```

Bit 2 is self BLE status; bit 3 is peer BLE status. Its effective truth table is:

| Self BLE status | Peer BLE status | Aggregate connected |
|---|---|---|
| 0 | 0 | false |
| 1 | 0 | false |
| 0 | 1 | false |
| 1 | 1 | true |

The bits are maintained by `UX_LocalSystemStatusSyncHandler` at `0x0047CF60`, using role-qualified status records over service `0x0103`. An aggregate transition emits `CB_EVENT_BLE_STATUS_CHANGE`. Consequently, changing from neither side connected to only one side connected does not change this aggregate boolean.

Sources: [UX system recovery, Status protocol](g2-ux-system-recovery.md), [UX function map](../../tools/manifests/g2-ux-system-function-map.tsv), [getter decompilation](../../research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-03.c) at lines 3138–3145. The getter was also checked directly against the reference image's Thumb instructions during this investigation.

### 3. The crossed-out phone graphic is controlled by that aggregate

Dashboard watchface layout 1 constructs an image from descriptor `0x00769E5C`, then shows its container when `UX_GetSystemBLEStatus()` is false and hides it when true. Layout 2 uses the same descriptor and condition. The recovered layouts 3 and 4 also call the same getter in their corresponding visibility logic.

The descriptor was inspected directly: it describes a 24×24 L8 image, with 576 pixel bytes at `0x006AB1C0`. Rendering those bytes confirms that the graphic is a **phone crossed out by a diagonal line**. Thus this is specifically evidence about the reported icon, rather than a similarly named battery or ring indicator.

Source: [watchface decompilation](../../research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-13.c), especially lines 14829–14857 and 15623–15652; [layout 1 recovery](g2-dashboard-watchface-layout1-recovery.md), [layout 2 recovery](g2-dashboard-watchface-layout2-recovery.md).

### 4. Stock already has a connection-triggered status notification

The connection-open branch schedules callback `0x0046F350` with value `1` after 3,000 ms. That callback forwards the value to `0x004B82E8`, which posts a role-qualified BLE status record through the local service `0x0103` path. The callback's final call was verified directly in the reference image. Another helper, `0x0046F32C`, publishes whether the raw connection ID at offset `0x54` is nonzero.

This means the evidence **does not establish that an app message is always required before BLE status can update**. There is already a path from link-open to a status notification. A missing peer connection/status, failed or stale synchronization, or a display/event-refresh issue remains a better-bounded set of hypotheses than claiming the dashboard necessarily waits for an app handshake.

Sources: [peripheral decompilation](../../research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-02.c) at lines 12734–12746 and 13315–13324; [peripheral function map](../../tools/manifests/g2-app-ble-peripheral-function-map.tsv), entries 30–31; [status publisher decompilation](../../research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-05.c) at lines 8531–8587.

### 5. Advertising and dashboard state are separate policies

The peripheral object owns advertising, connection, disconnect, and restart policy separately from UX status. Its disconnect branch schedules advertising restart work; its connection-open branch also contains timed work. The presence of an occupied raw link is consistent with the reported inability to connect from Android, but static analysis here does not prove which advertising or capacity condition persisted on the user's glasses.

Do not infer a permanent one-connection limit, an iOS-specific stack defect, or absence of retry/timeout handling from this report. The recovered Cordio adapter has a three-record connection table; that is not proof that three simultaneous phone connections are supported by product policy.

Sources: [peripheral recovery](g2-app-ble-peripheral-recovery.md), [Cordio slave adapter](../../components/shared/cordio/runtime_cordio_app_slave.c).

## Proposed fix direction

Add an on-glasses connection indicator driven by phone-facing link-open/link-close state, with distinct states for:

- No phone link.
- Phone link occupied / partial connection, including which glasses side is connected when known.
- Both sides connected; app readiness can be shown separately if the firmware has a reliable signal for it.

The local occupied-link indication must work before control-app traffic and should refresh on both connection events and dashboard entry. Peer status should distinguish unknown/stale information from a confirmed disconnection where feasible. A separate “ready for another phone” indication should use actual advertising/connection policy, because no app session does not imply availability.

Do **not** simply change `UX_GetSystemBLEStatus` from AND to OR globally: the getter has 33 recovered call sites, and feature gating may depend on both sides being connected. Introduce a separate UI-facing link/partial-state model while retaining the existing readiness semantics for its other consumers. An on-glasses disconnect/switch-phone action could be a separate usability improvement.

## Validation and remaining diagnosis

Acceptance checks for a fix:

1. Establish a phone-facing BLE link without sending control-app protocol messages. The glasses show that the link is occupied.
2. Exercise only one connected side, both connected sides, and delayed/missing peer status. Partial connection is distinguishable from no connection.
3. Repeat with the iPhone app foregrounded, backgrounded, and force-quit; record which conditions actually reproduce the issue.
4. Disconnect the phone and verify the occupied indication clears. Confirm that any availability indication agrees with actual Android discovery and connection behavior.
5. Enter/re-enter the dashboard and change watchface layouts while a partial connection exists. The indication must not depend solely on a previously delivered event.
6. Ensure a ring-only connection does not appear as a phone connection and that features requiring both glasses still use the appropriate readiness condition.

To identify the cause of the reported session, capture on **both sides**, with timestamps: connection-open/close events and IDs, raw context offset `0x54`, the 3-second status callback, service `0x0103` records, `0x20075043` before/after handling, emitted BLE status callbacks, and dashboard refresh. Record connectable advertising separately with an Android scan/controller trace. Observe through the existing 3-second status notification and 30-second scheduled work. This distinguishes a genuinely partial connection from a lost status update or stale UI.

Software verification performed: 18 existing tests passed across `test_analyze_g2_ux_system`, `test_analyze_g2_app_ble_peripheral`, and the four `test_analyze_g2_dashboard_watchface_layoutN` modules. These authenticate recovered objects and their recorded contracts against the reference image; they are not a hardware reproduction or proof of the iPhone-specific cause. The icon bytes and relevant Thumb instructions were independently inspected. No firmware code was changed and no device was flashed.
