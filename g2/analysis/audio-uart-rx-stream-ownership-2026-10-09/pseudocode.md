# RX-to-stream ownership

```c
// Original0x55E4EC; selected fields of channel records at20000D2C,stride28.
void channel_receive(uint32_t ch,uint32_t max_bytes,bool flush) {
    descriptor *d=channels[ch].queues; // +16; channel1d=20000CFC
    uint32_t count=0;
    fifo_read(channels[ch].handle,d->rx_storage+d->staged,max_bytes,&count);
    // HAL error return ignored here; count includes only valid stored bytes.
    d->staged+=count;                  // d+8
    if(flush) {
        if(channels[ch].callback)
            channels[ch].callback(d->rx_storage,d->staged);
        d->staged=0;
    }
}
// Actual callback0x5415E6 installed for channel1 by0x54171C.
void logger_rx_callback(const uint8_t *data,uint32_t count) {
    if(count) {
        int32_t woken=0;
        xStreamBufferSendFromISR(*(void **)0x200748BC,data,count,&woken);
        // Accepted-byte return is discarded. This body does not yield;
        // complete vector/caller scheduling has not been established.
    }
}
// Original0x57E05E, stock FreeRTOS10.5.1 source family.
size_t stream_send_isr(stream *s,const uint8_t *data,size_t count,int32_t *woken) {
    size_t required=count+(s->message_mode?4:0);
    size_t free=spaces(s);             // one reserved slot
    size_t accepted;
    if(s->message_mode) {
        accepted=free>=required?count:0;
        if(accepted)copy_ring_length_header(s,count);
    } else accepted=min(count,free);
    if(accepted) {
        copy_into_ring_then_publish_head(s,data,accepted);
        if(bytes_in_ring(s)>=s->trigger) {
            uint32_t saved=mask_basepri_30();
            if(s->waiting_receiver) {
                notify_from_isr(s->waiting_receiver,0,0,eNoAction,NULL,woken);
                s->waiting_receiver=NULL;
            }
            restore_basepri(saved);
        }
    }
    return accepted;
}
```

| Stage | Storage / ownership | Boundary |
|---|---|---|
| Hardware RX | UART1DR4003A000/FR4003A018 | Synthetic byte/status reads only; FIFO/error bytes from original instructions |
| Staging | Channel1pointer200B9C20, staged count at20000CFC+8 | FIFO read writes bytes here, threshold path accumulates15; timeout path requests16 then flushes |
| Callback | Pointer5415E7, handle global200748BC | Borrows staging only during synchronous send |
| Stream |36B control, tail0/head4/length8/trigger12/waitRecv16/waitSend20/buffer24/flags28/trace32 | Accepted bytes copied into ring; head published afterward |
| Receiver | Task notification0x455DC0 | Original/native before-call cuts and synthetic returns only; real wake/scheduling unresolved |

Logger create at0x54171C requests2048bytes,trigger1,stream-modefalse,callbacksNULL. Generic create0x57DEEA uses one heap allocation of2085bytes:36Bcontrol+2049Bstorage, usable capacity2048. Allocation provider is an explicit boundary, not full heap execution here; earlier native main-heap evidence remains preserved.

Message buffers use4byte lengths and all-or-nothing admission; stream buffers accept available prefix. Direct tests validate both, but logger is stream mode. Constructor assert-fill initializes storage0x55 and clears36Bcontrol; cfgtrace field is included, per-instance completion callbacks absent in the tested stock configuration.

Full stream pressure fixture: source205bytes,free2 →2copied/203discarded,staging count reset0. Empty real-sized stream accepts all205bytes. Reusing staging asZ immediately after callback changes no copied stream bytes. Controlled pressure is not evidence of actual hardware packet loss or a live overflow.
