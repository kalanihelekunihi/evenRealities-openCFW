# Semaphore and mutex source behavior

```c
bool take(q, wait_ticks) {
    assert(q && q.item_size==0);
    assert(!(scheduler_suspended && wait_ticks));
    bool inherited=false;
    for (;;) {
        critical_enter();
        if (q.available) {
            --q.available;
            if (is_mutex(q)) { ++current.held_mutexes; q.holder=current; }
            wake_highest_sender_and_request_yield_if_needed(q);
            critical_exit(); return true;
        }
        if (!wait_ticks) { critical_exit(); return false; }
        capture_timeout_once(); critical_exit();
        scheduler_suspend(); lock_queue(q);
        if (!timeout_expired(&wait_ticks)) {
            if (!q.available) {
                if (is_mutex(q)) inherited=inherit(q.holder);
                place_current_on_receive_waiters_and_delay(q,wait_ticks);
                unlock_queue(q); scheduler_resume(); request_yield_if_needed();
                // STOP: actual task/exception handover unmodeled
            } else { unlock_queue(q); scheduler_resume(); }
        } else {
            unlock_queue(q); scheduler_resume();
            if (!q.available) {
                if (inherited) timeout_disinherit(q.holder, highest_waiter(q));
                return false;
            }
        }
    }
}
unsigned highest_waiter(q) {
    return q.receive_waiters.count ? 56-q.receive_waiters.head.value : 0;
}
bool recursive_take(q, ticks) {
    if (q.holder==current) { ++q.recursion; return true; }
    bool ok=take(q,ticks); if (ok) ++q.recursion; return ok;
}
bool recursive_give(q) {
    if (q.holder!=current) return false;
    if (--q.recursion==0) give(q); return true;
}
```

CMSIS decode: `q=tagged_handle & ~1u`; low bit selects recursive take/give. Both wrappers reject IRQ-style context with-6 before null-handle check(-4). Acquire maps unavailable no-wait to-3 and positive-wait failure to-2; release maps kernel failure to-3. Actual kernel assertion is not converted to a CMSIS error. Values are signed32 statuses. IRQ context uses the previously recovered scheduler/mask rules, including pre-start mask behavior.
