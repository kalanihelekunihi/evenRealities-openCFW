# XTAL ownership and request control flow

Stock main load0x438000; exact body hashes in function-bindings.json. Names are recovered using pinned Ambiq HAL source; pseudocode preserves stock flow. Query/update/status/release helpers have native offline reconstructions; the request body below is pseudocode and an original-code dependency.

```c
// g_users at0x20073324: seven rows, two uint32_t words each.
// Valid users0..56; user52 => row2 high-word bit20 at0x20073338.
// Query functions byte-narrow but do NOT validate clock/user boundaries.
bool any(uint8_t clock) { return users[clock][0] || users[clock][1]; }
bool requested(uint8_t clock, uint8_t user) {
    return (users[clock][user >> 5] >> (user & 31)) & 1;
}
unsigned set(uint8_t clock, uint8_t user, uint8_t yes) {
    if (clock >= 7 || user >= 57) return 6;
    // yes==0 clears; every other byte sets. No reference count/lock here.
    update_bit(&users[clock][user >> 5], user & 31, yes != 0);
    return 0;
}

// 0x4C3D9E..0x4C3E9A; valid-user public dispatch0x4C44BC invokes it.
uint32_t xtal_request(uint8_t user) {
    uint32_t status = 0, counter = 150;
    if (*(uint32_t*)0x200001D0 == 0) return 7; // board XTAL frequency
    if (requested(2, user)) {
        mask = irq_save();
        if (stabilizing) counter = *counter_pointer;
        counter_pointer = &counter; // unconditional, even stabilizing==false
        irq_restore(mask);
        wait_xtal(&counter);
        return 0;
    }
    mask = irq_save();
    mode = xtal_status(); //0 off;1 internal crystal;2 external, control bit8 wins
    if (stabilizing) counter = *counter_pointer;
    if (mode == 0) {
        if (*(uint8_t*)0x200001CC == 1) oscillator(3, &true_byte);
        else { oscillator(2, NULL); if (!stabilizing) stabilizing = true; }
    } else if (mode==2 && board_mode==0) status=3;
    else if (mode==1 && board_mode==1) status=3;
    if (status==0) set(2, user, true);
    if (stabilizing) counter_pointer = &counter;
    irq_restore(mask);
    wait_xtal(&counter);
    return status;
}

// 0x4C3D70..0x4C3D9E; flag0x20074F56, pointer0x20074260.
void wait_xtal(uint32_t *counter) {
    if (!stabilizing) return;
    while (*counter && stabilizing) { delay_api(10); --*counter; }
    mask = irq_save();
    stabilizing = false; counter_pointer = NULL;
    irq_restore(mask);
}
// No hardware-ready bit checked and no timeout error returned by this wait.
// API source identifies microseconds; physical delay accuracy is unverified.

// 0x4C3E9A..0x4C3EF4: native audio_xtal_release models complete body.
uint32_t xtal_release(uint8_t user) {
    if (!requested(2,user)) return 0;
    mask = irq_save(); set(2,user,false);
    if (!any(2)) {
        oscillator(4,&true_byte); // status ignored
        stabilizing=false; counter_pointer=NULL;
    }
    irq_restore(mask); return 0;
}
```

Public request/release dispatchers narrow clock/user to bytes, reject narrowed user>=57, and dispatch clock0..6; invalid clock returns6. XTAL child itself expects a valid user. No arbitrary out-of-range query may be treated as a supported interface.

Counter-pointer ownership: a repeat request can leave a pointer to its returned stack local while stabilizing is false. Subsequent consumers shown here dereference it only under stabilizing. Last-user release clears both; release with another user preserves the inactive pointer. This is observed software state, not proof of an active use-after-return or hardware hazard. A concurrency claim requires actual IRQ/caller sequencing.
