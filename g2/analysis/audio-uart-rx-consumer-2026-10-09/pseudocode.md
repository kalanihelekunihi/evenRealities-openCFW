# Consumer/staging pseudocode

```c
receive(stream, dst, capacity, ticks0) {
    available = ring_distance(head, tail);
    if (message_mode) {
        if (available <= 4) return 0;
        next_tail = peek_copy_length_header(tail);
        wanted = next_length > capacity ? 0 : next_length;
        available -= 4;
    } else { next_tail=tail; wanted=capacity; }
    count=min(wanted,available);
    if (!count) return 0; // no tail commit
    tail = copy_wrapped_to_caller(dst,count,next_tail);
    scheduler_suspend();
    if (waiting_sender) { notify_sender(); waiting_sender=NULL; }
    scheduler_resume(); return count;
}
uart3_put(q, byte) {
    if (((q.write-q.read)&q.mask)==q.mask)
        q.read=(q.read+1)&q.mask; // evicts oldest
    q.storage[q.write]=byte;
    q.write=(q.write+1)&q.mask;
}
```

Copied consumer bytes are caller-owned independently of later ring reuse. Message header peek does not consume when capacity insufficient. Scheduler calls shown are stub/cut boundaries in current fixtures, not proven task handover.

UART3 staging63usable at200731B0; descriptor20073ED4. Protocol stream global20074B14 has24576usable bytes. Logger streamglobal200748BC has2048usable bytes. TXqueue1024 at200BA420 is another separate store. Full stream admission rejects incoming suffix; full UART3 ring evicts oldest. No live loss measurement.
