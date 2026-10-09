# Pool ownership and heap behavior

```c
Pool *new_pool(count, requested_size, attr) {
    if (IRQ_context() || !count || !requested_size) return NULL;
    array_bytes = count * ((requested_size+3u)>>2) * 4u;
    // Attribute classification controls heap flags; malformed nonnull
    // attributes can still flow through the static-pointer branch.
    p = dynamic_cb ? heap_allocate(116) : attr.cb_mem;
    p.sem = counting_semaphore_static(count,count,&p.embedded_sem);
    p.array = dynamic_array ? heap_allocate(array_bytes) : attr.mp_mem;
    p.head=NULL; p.created=0; p.stride=requested_size; p.count=count;
    p.array_bytes=array_bytes; p.status=0x5EED0000|heap_flags;
    return p;
}
void *alloc(p, ticks) {
    if (!p || !valid(p.status)) return NULL;
    if (IRQ_context() && ticks) return NULL;
    if (!take_availability_semaphore(p.sem,ticks)) return NULL;
    if (!valid(p.status)) return NULL; // token is not refunded here
    enter_task_or_ISR_critical();
    if (p.head) { result=p.head; p.head=result.next; }
    else if (p.created<p.count) result=p.array+p.stride*p.created++;
    else result=NULL;
    leave_critical(); return result;
}
int free(p, block) {
    if (!p || !block) return -4;
    if (!valid(p.status)) return -3;
    if (block<p.array || block>p.array+p.array_bytes-1u) return -4;
    if (semaphore_count(p.sem)==p.count) return -3;
    enter_task_or_ISR_critical();
    *(void**)block=p.head; p.head=block;
    leave_critical(); give_availability_semaphore(p.sem);
    return 0;
}
```

Free does not test slot alignment, whether a slot was allocated, or duplicate membership. The free link occupies the first four bytes; remaining bytes are not cleared. Lifecycle tests with valid multiple-of-four strides show LIFO reuse. Separate interior/last-byte/duplicate-free tests are synthetic misuse evidence, not a claim of valid API behavior or a live hardware fault.

Heap block header: next pointer0,size4; high size bit means allocated. `wanted>0` is charged `wanted+16-(wanted&7)` with overflow rejection; leftover is split only when strictly greater than16. Allocation chooses first address-ordered fitting block; free clears the high bit and merges adjacent free blocks. Initial usable size is192504 bytes from the configured0x2F000-byte heap. A fresh synthetic heap accepts requested192495 but rejects192496; live free/fragmentation state is not established.

Allocation failure invokes the failure callback; logger disabled returns0, callback then enters an actual self-loop. Enabled logger prepares buffer0x2006B930 and format0x758F70 for formatter0x473036, where execution stops. No formatter result or sink call is fabricated. Failure therefore does not establish a returned NULL in stock behavior.
