# Non-UART event schema/callback-root constraints

Existing codec.tsv historical trigger/tick/startup names and evidence consulted first. Prior packets already name functions; no new function identification claimed. Source-opportunities ledger retains schema/root binding lead. No matching exact names/addresses in current117task contracts; bounded ownership check does not prove all external/live vacancy. Read-only static source/layout comparison only; no execution, new reconstruction or campaign mutation.

## Byte authentication and exact static references

Canonical XIP49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584, conditional runtime base10203004. Trigger20bytes, Tick80bytes and existing initializer116bytes independently match codec.tsv hashes; event-schema-byte-bindings.json retains raw slices and source hashes. Existing full-XIP decode identity is in consumed-disassembly.json. Original artifacts untouched; no failed coordinate conversions in this follow-up.

Trigger10208CC0 moves input pointer to r1, loads queue address2002ECD8 into r0, calls existing QueuePut100261B8, returns0. No event-id filtering or second queue call appears in this bounded body.

Initializer10208CD4 loads queue2002ECD8, buffer2002E880, buffer length64 and item size8 before existing QueueInit10206F9C. Source APP_EVENT is two32bitwords event_id/ctx_index; public misc queue capacity8 produces64bytes. This binds queue event-item layout through explicit caller constants, not from name alone. Exact capacity usable-slot behavior belongs to previously mapped queue implementation and is not newly tested.

Tick10208D48 reserves8bytes and zeroes both event words; passes SP and queue2002ECD8 to QueueGet10206FB0. On nonzero dequeue, loads pointer from20026D38, guards it and field+8, then calls field+8 with event pointer. Separately guards the same root pointer and field+12 and calls it with no new argument setup. These offsets align with LVP_APP.AppEventResponse and AppTaskLoop. Concrete descriptor pointer and function-pointer VALUES are not identified by reading the slot address; no current/initialized runtime contents are assumed. Source lvp_app.h defines a strong root via LVP_REGISTER_APP, while core source weak root defaultsNULL. Producing application's override/link initializer or independently mapped data initialization is the next evidence for actual callback target addresses.

Existing suspend/resume wrapper references at10208CA0/10208C7C also align with LVP_APP+16/+20 and+24/+28; these support layout but do not establish runtime calls.

## Configuration/source equivalence classes

Pinned KWS8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5 lvp_app_core.c:105+ and231+ match the single misc-queue schema with G-sensor guard/AIN auxiliary path absent in these bodies. In unchanged KWS source, LVP_APP_ENABLE_AIN_CB_EVENT is enabled by G_SENSOR_VAD or UART_RECORD_ENABLE; absence constrains that local preprocessed path, not global availability of audio/UART hardware. Closed UART path is not reopened.

Tick's tail calls existing historical watchdog-ping target102067A0 after optional queue/callback work (original call10208D84). KWS source has CONFIG_LVP_HAS_WATCHDOG_TICK_BLOCK ping at function tail. AIoT d4aa00943e22f9ddfa424f979fae3ee2a62f5c0b puts optional ping inside successful QueueGet branch and has no tail ping. Therefore unchanged AIoT's source structure is incompatible with the observed watchdog placement under normal effect-preserving lowering; KWS-like path remains supported. This is not a compiler-byte rebuild or unique revision attribution. Modified descendants/private code remain alternatives. AppEventResponse/TaskLoop layout and queue schema are shared and cannot discriminate source family alone.

The other direct tail call10208334 is already mapped UART lifecycle; it is retained as a boundary/reference only, not analyzed or credited here. No physical callback, queue population, watchdog delivery, runtime reachability or concurrency is inferred from these static references.

## Stop/next evidence

Closed local source-backed event size, queue-buffer/init constants, callback field offsets and watchdog placement constraint. Remaining callback target binding needs authenticated app_core_ops static initializer/strong override or genuine initialization-store evidence, not guessed public app names or live-state assumptions. Exact producing source pin/configuration still requires compiler/source comparison or build manifest; shared schema is not source completeness. No new download, byte export beyond small code receipts, device access, canonical/index edits or admission.
