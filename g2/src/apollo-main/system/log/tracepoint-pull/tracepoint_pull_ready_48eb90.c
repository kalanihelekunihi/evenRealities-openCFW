/* Stock Main 0x48eb90: drain the persistent record ring before a pull. */
#include <stdint.h>

extern volatile uint8_t audio_uart_ring_persist_initialized;
extern volatile uint8_t audio_uart_ring_persist_wake_blocked;
extern volatile uint8_t audio_uart_ring_persist_wake_pending;
extern uint8_t audio_uart_ring_persist_queue_state[24u];
extern void audio_uart_ring_persist_initialize_48eac8(void);
extern uint32_t audio_uart_ring_persist_record_size_48e8f0(uint32_t);
extern uint32_t audio_uart_ring_persist_read_word_48e8e2(uint32_t);
extern void audio_uart_ring_persist_submit_48ea66(uint32_t,uint32_t,const void *);
extern int32_t audio_tracepoint_pull_backend_init_47dfec(void);
extern int32_t audio_tracepoint_pull_write_batch_47e178(const void *,uint32_t);
extern void audio_tracepoint_pull_complete_47e220(void);

volatile uint8_t audio_tracepoint_pull_backend_ready_20075035
    __attribute__((section(".bss.opencfw.tracepoint.pull_backend_ready"),used));
uint32_t audio_tracepoint_pull_failure_count_20074ac0
    __attribute__((section(".bss.opencfw.tracepoint.pull_failure_count"),aligned(4),used));

static uint32_t disable_irq(void) {
    uint32_t saved;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(saved) :: "memory");
    return saved;
}
static void restore_irq(uint32_t saved) {
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
}
static uint32_t word(const uint8_t *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)(p+offset);
}
static void put(uint8_t *p,uint32_t offset,uint32_t value) {
    *(uint32_t *)(void *)(p+offset)=value;
}

int32_t audio_tracepoint_pull_ready_48eb90(void) {
    if(audio_uart_ring_persist_initialized==0u)
        audio_uart_ring_persist_initialize_48eac8();
    uint32_t saved=disable_irq();
    if(audio_uart_ring_persist_wake_blocked!=0u) {
        restore_irq(saved);
        return -16;
    }
    audio_uart_ring_persist_wake_blocked=1u;
    audio_uart_ring_persist_wake_pending=0u;
    restore_irq(saved);

    int32_t status=0;
    if(audio_tracepoint_pull_backend_ready_20075035==0u) {
        status=audio_tracepoint_pull_backend_init_47dfec();
        if(status!=0) {
            audio_tracepoint_pull_failure_count_20074ac0++;
            audio_uart_ring_persist_wake_blocked=0u;
            return status;
        }
        audio_tracepoint_pull_backend_ready_20075035=1u;
    }

    saved=disable_irq();
    uint32_t pending=word(audio_uart_ring_persist_queue_state,20u);
    put(audio_uart_ring_persist_queue_state,20u,0u);
    restore_irq(saved);
    if(pending!=0u)
        audio_uart_ring_persist_submit_48ea66(0xffff82u,1u,&pending);

    for(;;) {
        uint32_t batch[16];
        saved=disable_irq();
        uint32_t cursor=word(audio_uart_ring_persist_queue_state,16u);
        uint32_t end=word(audio_uart_ring_persist_queue_state,8u);
        uint32_t bytes=0u;
        while(cursor+bytes!=end) {
            uint32_t next=audio_uart_ring_persist_record_size_48e8f0(cursor+bytes);
            if(next+bytes>=65u) break;
            bytes+=next;
        }
        for(uint32_t offset=0u;offset<bytes;offset+=4u)
            batch[offset/4u]=audio_uart_ring_persist_read_word_48e8e2(cursor+offset);
        put(audio_uart_ring_persist_queue_state,16u,cursor+bytes);
        restore_irq(saved);
        if(bytes==0u) break;
        status=audio_tracepoint_pull_write_batch_47e178(batch,bytes);
        if(status!=0) {
            audio_tracepoint_pull_failure_count_20074ac0++;
            break;
        }
    }
    audio_tracepoint_pull_complete_47e220();
    audio_uart_ring_persist_wake_blocked=0u;
    return status;
}
