# Offline timer wake providers

[Analysis and tests](../../../analysis/audio-timer-wake-provider-closure-2026-10-08/REPORT.md). `unlock.c` is the preserved public FreeRTOS selected body, MIT license retained; it requires scheduler suspension and valid ARM32 intrusive lists. `port.c` and `sorted.c` are reconstructed C/architectural operations from authenticated stock instructions. `unlock.h` exposes the offline queue interface. They are knowledge/test artifacts, not production firmware or a live-safe lifetime patch.

Public ready/list source is linked unchanged from `components/foundation/freertos_ready`. Full TCB/exception delivery is not supplied. All native valid wake/unlock/restricted-wait fixture instructions remain in native code; delete integration deliberately retains original queue/allocator peers. Zero-nesting critical exit and invalid waiter assertions stop before fatal continuations.
