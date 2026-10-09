# ISR queue/semaphore pseudocode

```c
bool receive_from_isr(q, output, woke) {
    assert(q && (output || q.item_size==0));
    saved=mask_api_interrupts();
    if (!q.count) { restore_mask(saved); return false; }
    copy_item_out_and_advance_read_cursor(q,output); --q.count;
    if (q.rx_lock==-1) {
        if (q.send_waiters && wake_sender(q) && woke) *woke=1;
    } else if ((unsigned)q.rx_lock < task_count) {
        assert(q.rx_lock!=127); ++q.rx_lock;
    }
    restore_mask(saved); return true;
}
bool give_from_isr(q,woke) {
    assert(q && q.item_size==0 && !is_held_mutex(q));
    saved=mask_api_interrupts();
    if (q.count==q.capacity) { restore_mask(saved); return false; }
    ++q.count;
    if (q.tx_lock==-1) {
        if (q.receive_waiters && wake_receiver(q) && woke) *woke=1;
    } else if ((unsigned)q.tx_lock < task_count) {
        assert(q.tx_lock!=127); ++q.tx_lock;
    }
    restore_mask(saved); return true;
}
```

`woke` is not initialized by kernel APIs and never cleared on failure/no-wake; callers normally initialize zero. CMSIS wrappers do. `woke=1` requires strictly higher priority than current; suspended scheduler uses pending-ready handling, not proven actual scheduling.

CMSIS semaphore acquire first rejects null(-4). IRQ-style nonzero timeout also returns-4. IRQ-style no-wait calls receive(q,NULL,&woke), maps empty to-3, and writes PendSV set-bit only on successful wake. Task route calls semaphore-take, mapping false to-3(no-wait) or-2(positive-wait). Release rejects null(-4), maps full to-3 and uses give-from-ISR in IRQ context or generic task send otherwise. Successful status is0. Raw semaphore handles are not tagged recursive mutex handles.
