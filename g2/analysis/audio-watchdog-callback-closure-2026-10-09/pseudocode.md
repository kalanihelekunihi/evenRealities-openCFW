# Watchdog message path

```c
void timer_callback(void *ignored) { //0x53C2A4
    Message message = {6,0,0};
    publish(&message); //0x53C638 → actual queue put0x449ABE
}
void type6_log_disabled(Message *ignored) { //0x53C92E selected mask0
    if (!enabled_byte) return;
    uint32_t prior = consumed_counter;
    consumed_counter = 0;
    read_real_log_mask_three_times(); // each actual read must0
    if (prior < 20) emit_type0(2);
}
void emit_type0(uint32_t value) { //0x53CA10
    Message message = {0,1,(uint8_t)value}; publish(&message);
}
```

Message layout12 bytes: u32 type0,mode4,value8; little endian. Publisher copies into the queue synchronously before it reaches thread-flag set0x400000. The stack message is not retained as a borrowed pointer by the reached queue-copy path. This does not establish eventual consumption: queue-full drops and a successful copied queue entry can still await scheduling.

Enabled0x2007502E,counter0x20074A9C. The counter tracks the previous period's PCM-consumer increments; no byte/sample/time conversion is derived here. Logger-enabled formatting/routing branches are omitted by contract, not fabricated as successful no-ops.
