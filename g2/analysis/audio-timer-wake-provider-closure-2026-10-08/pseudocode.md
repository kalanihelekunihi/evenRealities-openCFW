# Event wake and deferred queue unlock

```c
bool event_unblock(List *events) { //0x455370, caller holds critical section
    Task *t = events->head.owner; // initialized, nonempty list required
    remove(t->event);
    if (scheduler_suspended == 0) {
        remove(t->state); ready_insert(t->priority, t->state);
        next_unblock_tick = delayed.empty ? UINT32_MAX : delayed.head.value;
    } else {
        pending_ready.insert_before_index(t->event); // state remains blocked
    }
    if (t->priority > current->priority) { yield_pending=1; return true; }
    return false;
}
void unlock(Queue *q) { //0x441F88, scheduler suspended required
    enter_critical();
    int8_t local_tx_lock=q->tx_lock;
    while (local_tx_lock > 0 && !q->receivers.empty) {
        if (event_unblock(q->receivers)) missed_yield();
        --local_tx_lock; // queue byte published as -1 after loop
    }
    q->tx_lock = -1; exit_critical();
    enter_critical();
    int8_t local_rx_lock=q->rx_lock;
    while (local_rx_lock > 0 && !q->senders.empty) {
        if (event_unblock(q->senders)) missed_yield();
        --local_rx_lock;
    }
    q->rx_lock = -1; exit_critical();
}
```

Loop pseudocode uses the signed local copy of each lock throughout the loop; it does not repeatedly test the queue byte. Actual readable body is [unlock.c](../../components/audio/timer_wake_providers_offline/unlock.c).

TCB accessed prefix: stack pointer0; state item4; event item24; priority44. Item20 bytes: value0,next4,previous8,owner12,container16. List20 bytes: count0,index4,sentinel8. Queue: sender list16,receiver list36,count56,length60,item-size64,RX lock68,TX lock69. A full stock TCB is112 bytes; the48-byte prefix is not an allocation size.

Critical entry sets BASEPRI0x30, increments uint32 nesting0x2000309C, then DSB/ISB. It does not preserve the previous mask for the outermost exit. Valid exit decrements nesting and clears BASEPRI when it reaches0. Zero-nesting exit reaches a fatal continuation; tests stop before its store to0xFFFFFFFF. Mask-set returns the previous mask but sets the threshold exactly, rather than BASEPRI_MAX. Missed yield only writes1 to0x20074A44; it does not switch tasks.

Sorted insertion places equal values after existing peers. UINT32_MAX inserts after the tail directly so sentinel equality cannot make traversal loop forever. Removal adjusts index to previous item if it pointed at the removed item; container becomesNULL.
