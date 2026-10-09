# Recovered task-mutex behavior

```c
bool inherit(holder) {
    if (!holder) return false;
    if (holder.priority < current.priority) {
        if (!(holder.event.value & 0x80000000))
            holder.event.value = 56-current.priority;
        bool ready = holder.state.container == ready[holder.priority];
        if (ready) remove(holder.state);
        holder.priority = current.priority;
        if (ready) append(ready[holder.priority], holder.state);
        return true;
    }
    return holder.base_priority < current.priority;
}
bool release_disinherit(holder) {
    if (!holder) return false;
    assert(holder==current && holder.mutexes_held!=0);
    --holder.mutexes_held;
    if (holder.priority==holder.base_priority || holder.mutexes_held) return false;
    remove(holder.state);
    holder.priority=holder.base_priority;
    holder.event.value=56-holder.priority;
    append(ready[holder.priority],holder.state);
    return true; // caller may request yield; no actual context switch proved
}
void timeout_disinherit(holder, highest_remaining_waiter) {
    if (!holder) return;
    assert(holder.mutexes_held!=0);
    unsigned target=max(holder.base_priority,highest_remaining_waiter);
    if (holder.priority==target || holder.mutexes_held!=1) return;
    assert(holder!=current);
    unsigned old=holder.priority;
    holder.priority=target;
    if (!(holder.event.value&0x80000000)) holder.event.value=56-target;
    if (holder.state.container==ready[old]) {
        remove(holder.state); append(ready[target],holder.state);
    }
}
```

Ready insertion raises the cached top-ready priority if needed. Removal does not immediately lower it in this stock configuration; scheduler search is outside these routines. Blocked-holder state-list position stays unchanged while priority/event value changes. These routines do not convert tick units, allocate/free memory or themselves deliver exception return.
