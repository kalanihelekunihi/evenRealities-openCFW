# Boundary and scheduler fields

```c
if (PC == 0x4420BC) { // before any port-yield instruction
    record(queue_count, active_timer_count, suspend_count, task_count);
    stop_execution(); // no PendSV delivery or fabricated return
}
```

Port-yield0x4420BC stores0x10000000 toICSR, executesDSB/ISB and returns at instruction level. This is a request for PendSV, not a standalone implementation of task handover. Suspension count:0x20074A58; current task count:0x20074A30. The semantic correction is additive; earlier source,ELF,results and seals remain intact.
