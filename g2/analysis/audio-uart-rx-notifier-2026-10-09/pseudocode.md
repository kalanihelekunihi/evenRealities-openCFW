# Valid-task ISR notify0x455DC0

TCB fields: state-list item+4; event-list item+24; event container+40; priority+44; notification value+104; state byte+108. List20B: count0,index4,end sentinel8,next12,prev16.

Globals: currentTCBpointer20074A20; scheduler-suspended20074A58; top-ready-priority20074A38; readylistbase2006A49C,stride20; pending-ready20073D24; yield-pending20074A44.

```c
oldmask=raise_BASEPRI_30();
if (previous) *previous=notify_value;
oldstate=notify_state; notify_state=2;
apply_action_0_to_4();
if (oldstate==1) {
    assert(event_container==NULL);
    if (!scheduler_suspended) {
        unlink(state_item); update_top_ready_priority();
        insert_end(ready[task.priority],state_item);
    } else insert_end(pending_ready,event_item);
    if (task.priority>current.priority) {
        if (woken) *woken=1; yield_pending=1;
    }
}
restore_BASEPRI(oldmask); return action_success;
```

No PendSV register write in this provider or bounded logger callback compositions. Suspended-state pending-ready item does not itself remove delayed item. Running ready insertion is software list state, not proof a context switch ran. Subsequent resume/ISR-exit port behavior remains a separate source lead.
