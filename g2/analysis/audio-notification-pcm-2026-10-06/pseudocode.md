# Notification to PCM boundary

Manual reconstruction of authenticated Apollo Thumb instructions, load0x438000 after32-byte OTA header. Numeric names here are observations, not recovered original source types. Implementation seams return new observation records at provider cuts; stock ABI returns are not invented.

```c
//53c6b2
message = { .type=2, .reserved=0, .tick=osKernelGetTickCount() };
AUD_SendMessage(&message);
//53c638
if (!message || !audio_state.queue) return;
status=osMessageQueuePut(audio_state.queue,message,0,0);
if (status!=0) { /*43d0ce logging boundary*/ return; }
osThreadFlagsSet(audio_state.thread,0x400000); //449238 external scheduling boundary
```

The message is12 bytes. ISR queue submission copies these12 bytes into queue storage; it does not copy PCM or save a DMA address. Queue acceptance and reaching the thread-flags call do not prove a waiting thread was unblocked. On full queue the new notification is rejected, and the wake provider is not called. Existing queued notifications are retained.

```c
//53cd62 static drain, not task-scheduling execution evidence
while (osMessageQueueGet(audio_state.queue,&message,NULL,0)==0)
    aud_dispatch(&message); //53c5ac searches8 rows atRAM20073fbc
//53cdac: actual shifts inspect flags bit22 / bit23, not bits9 /8
if (flags & 0x400000) drain();
if (flags & 0x800000) exit();
```

The dispatcher table has8-byte rows with uint16 type at+0 and function pointer at+4. Its actual initialized RAM contents and the thread-flags wait/set provider remain outside this batch. The end-to-end scenarios explicitly invoke the consumer after successful zero-wait receive; this is synthetic task scheduling, not execution of the actual audio task/dispatcher.

```c
//53c6f2
uint32_t sent=message->tick;
uint32_t age=osKernelGetTickCount()-sent; //unsigned32-bit modular subtraction
if (age>=41) { /*43d0ce logging boundary*/ return; }
uint32_t pcm=0,length=0;
get_rx_buffer(&pcm,&length); //57a7e0 queries590b6c, invalidates475014, publishes
++*(uint32_t *)0x20074a9c;
SVC_PcmAppProcessData(0,pcm,length); //57adf8
```

Ages0..40 ticks pass;41 and larger reject. Crossing UINT32 rollover is handled by modular subtraction. A timestamp numerically ahead of `now` can produce a huge unsigned age and reject. No tick-to-millisecond conversion is established here. The activity word increments after buffer publication, before PCM service, even when the service later rejects null PCM.

```c
//57adf8 through57ae56 or callback entry
uint8_t mode=(uint8_t)arg0;
if (mode>=2 || !pcm || !length) return;
record=(uint8_t *)0x20073c20+12*mode;
if (*(uint32_t *)(record+8)!=0 && record[4]==mode) {
    callback=*(uint32_t *)(record+8); //a real second read
    callback(mode,pcm,length); //stop before actual callback entry
    return;
}
if (mode==0) {
    //57ae56: stock LC3/algorithm/205-byte body fallback; not reimplemented here
}
```

Record+0..3/+5..7 semantics are not inferred. Mode0 missing or mismatched registration chooses DSP fallback; mode1 returns. Stock does not take a PCM copy or transfer ownership before either boundary. A nonzero callback first read is not a synchronized registration snapshot: it rereads the pointer before BLX. Mutation fixtures demonstrate this ordering, not a field race.

The tick/context wrappers are reconstructed actual RAM reads: scheduler-running20074a3c, suspended20074a58, tick20074a34. IRQ_Context returns1 for nonzeroIPSR; with scheduler state1 it returns0; otherwise PRIMASK/BASEPRI nonzero imply1. Both tick providers read the same tick word. This establishes neither tick increment nor scheduler/task-switch behavior.
