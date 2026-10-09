# UART TX lifetime and stock initialization

```c
// Stock 0x58DEF2 transaction-save.
uint32_t save_tx(state *s,const transfer *t) {
    uint32_t mask=disable_irq_save();
    if(s->writing) {restore_irq(mask);return 0x8000004;}
    s->writing=1;
    s->active.type=t->type;
    s->active.data=t->data; // borrowed, no copy here
    s->active.count=t->count;
    s->active.bytes_out=t->bytes_out;
    s->active.timeout=t->timeout;
    s->active.callback=t->callback;
    s->active.context=t->context;
    s->active.error=t->error;
    s->written=0;s->last_tx_complete=0;
    restore_irq(mask);return 0;
}
// Stock 0x58E4E8; initialize count-out even before busy rejection.
uint32_t nonblocking_tx(state *s,const transfer *t) {
    if(t->bytes_out)*t->bytes_out=0;
    uint32_t status=save_tx(s,t);
    if(status)return status;
    service_tx(s);return 0;
}
// Stock 0x58E454.
uint32_t blocking_tx(state *s,const transfer *t) {
    uint32_t status=nonblocking_tx(s,t),elapsed=0;
    if(status)return status;
    while(s->writing) {
        service_tx(s);delay_us(1000); // delay mocked in dynamic tests
        if(t->timeout!=UINT32_MAX && ++elapsed==t->timeout) {
            s->writing=0;return 4;
        }
    }
    return 0;
}
// Stock 0x58E534, with actual queue-add0x530084 / get0x5300E2.
void service_tx(state *s) {
    if(s->writing) {
        mask=disable_irq_save();
        uint8_t *src=s->active.data+s->written;
        size_t left=s->active.count-s->written;
        if(s->tx_queue_enabled) {
            count=min(left,queue.capacity-queue.length);
            ok=queue_add(&queue,src,count); // synchronously copies bytes
            if(!ok) {
                s->writing=0;
                if(callback) {callback(1,context);restore_irq(mask);return;}
            }
        } else count=fifo_write(src,left); // synchronously reads caller bytes
        s->written+=count;
        restore_irq(mask);
        if(bytes_out)*bytes_out=s->written;
        if(s->written==s->active.count && s->writing) {
            s->writing=0;if(callback)callback(0,context);
        }
    }
    if(s->tx_queue_enabled)queue_to_fifo(s);
}
```

Actual callbacks under queue failure are inside the critical section; successful-consumption callbacks are after restoring mask. Dynamic ordinary queues do not force the impossible-under-fixture capacity-check/add-failure race; no new scheduling claim.

| Data | Offset / identity | Ownership |
|---|---|---|
|Transfer input|56B; source0,count4,out8,timeout12,callback16,context20,type52|Caller owns structure/source; selected fields copied into state|
|UART state|284B stride; module40,TXqueue52,activeTX160,written216,queueenabled220,lastTXcomplete222,writing281|HAL-owned fixed global states at2006A02C|
|Queue|24B: write0/read4,length8,capacity12,itemsize16,data20|Caller supplies storage; queue_add copies bytes, no allocation|
|FIFO|module1base4003A000; DR0,FR24/TXFFbit5|MMIO consumption boundary, no physical-output proof|
|Channel1 marker|20000D2C+28+25|Set by original interrupt wrapper when supplied status bit0 is set|

**Copy/borrow cases:** direct FIFO partial: initialab copied, overwrite source toZZZZZ, resumed service producesabZZZ. Queue partial capacity2 behaves likewise for unconsumed bytes. Queue complete capacity8 with FIFO blocked:abcde copied,writing flag clears; overwrite source then drain still producesabcde. These deliberately controlled mutations demonstrate interface contracts, not a proved live misuse.

**Initialization:** original scatter decoder0x43A11E receives record0x75D3F4, expands10864 stored bytes at0x79189E into17752 bytes at20000000. Its output matches instruction-stepped execution. Channel1 descriptor module1,handle0,pin table786060,configuration20000CCC,queue descriptor20000CFC. TX capacity/pointer0/0; RX capacity0 with unused pointer200B9C20. Original init wrapper0x55E388 passes zeroTXpointer/size and zeroRXpointer/size for channel1. Module3 instead receives1024byteTX storage at200BA420.

Channel1 raw UART configuration's first16bytes encode baud921600,data bits enum3,parity2,stop0,flow0,TX/RX threshold enums2/2,clock0. The pinned header identifies8data bits/no parity/one stop/HFRC; no measured bitrate or clock state. Pin table words12,14,5,5 establish logical indexes/config words, not observed pad signals.

Original0x55E388 initializes eligible channels1/2/3 then invokes shutdown0x55E630, leaving active flags0. Caller0x5093AC later invokes0x55E5BC(1), which requests power and configures pads then sets channel1active=1. These latter hardware operations are static evidence or explicit success stubs, not verified physical activation.
