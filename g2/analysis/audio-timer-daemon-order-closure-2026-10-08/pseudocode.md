# Timer daemon flow and ownership boundary

```
daemon forever:
  expiry = next_expiry(&empty)
  process_or_block(expiry,empty)
  drain_commands()                 // after callback, not before expiry selection

process_or_block(expiry,empty):
  suspend_scheduler()
  now = sample_time(&switched)
  if switched: resume_scheduler()
  else if !empty && now>=expiry:
    resume_scheduler()
    expired(expiry,now)
  else:
    if empty: empty = overflow_list.count==0
    restricted_queue_wait(queue,uint32(expiry-now),empty)
    if !resume_scheduler(): yield()

expired(expiry,now):
  timer = current_list.head.owner
  remove(timer.item)
  if autoreload: original_reload(timer,expiry,now)
  else: clear timer.active
  timer.callback(timer)            // actual adapter reads ID&~1 then arg/callback

sample_time(&switched):
  now = actual_tick_reader()
  if now<last: actual_switch_lists(); switched=1
  else: switched=0
  last=now; return now
```

Queued command owns copied16 bytes andborrowed timer pointer. Delete publication may free auxiliary early; daemon ordering does not inspect that ownership bit before expiry. Tests stop at user callback entry or empty-queue blocking entry instead of supplying fabricated returns. The original providers remain actual code; pending scheduling/IRQ/callback-lifetime conclusions need real state/trace. No patch is supplied.
