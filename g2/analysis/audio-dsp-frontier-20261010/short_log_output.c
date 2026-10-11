#include <stdint.h>

extern void *audio_log_lock_state;
extern uint32_t audio_log_ring_state[4]; /* base, capacity, read, write */
extern int32_t audio_log_lock(void *state, uint32_t timeout);
extern void audio_log_unlock(void *state);
extern uint32_t audio_log_flags(void);
extern int32_t audio_log_flush_ready(void);
extern int32_t audio_log_flush_busy(void);
extern void audio_log_flush_notify(void);

/* Stock 0x43ca50 local ring-copy/flush policy. External sync/flush bodies
 * and initialized RAM remain separate providers. */
void audio_log_short_output(const void *message, uint32_t raw_length) {
    const uint8_t *input=(const uint8_t *)message;
    uint32_t length=(uint16_t)raw_length;
    uint32_t base=audio_log_ring_state[0],capacity=audio_log_ring_state[1];
    uint32_t flush=0;
    uint32_t ipsr;
    __asm volatile("mrs %0, ipsr" : "=r"(ipsr));
    if (ipsr || !audio_log_lock_state) return;
    if (audio_log_lock(audio_log_lock_state,500)!=1) return;
    uint32_t read=audio_log_ring_state[2],write=audio_log_ring_state[3];
    if (capacity>=read && capacity>=write) {
        uint32_t free=(write<read)?(read-write-1u):(read+capacity-write-1u);
        if (length>=free) flush=1;
        else {
            uint8_t *buffer=(uint8_t *)(uintptr_t)base;
            uint32_t until_wrap=capacity-write;
            if (until_wrap>=length) {
                for (uint32_t i=0;i<length;i++) buffer[write+i]=input[i];
            } else {
                for (uint32_t i=0;i<until_wrap;i++) buffer[write+i]=input[i];
                for (uint32_t i=0;i<length-until_wrap;i++) buffer[i]=input[until_wrap+i];
            }
            write=(length>=until_wrap)?(length-until_wrap):(write+length);
            audio_log_ring_state[3]=write;
            uint32_t flags=audio_log_flags();
            if (flags&4u) {if (capacity-free>=236u) flush=1;}
            else if (audio_log_flags()&1u) {if (capacity-free>=4096u) flush=1;}
        }
    }
    audio_log_unlock(audio_log_lock_state);
    if (flush) {
        if (audio_log_flags()&1u) {
            if (!audio_log_flush_ready() || !audio_log_flush_busy())
                audio_log_flush_notify();
        }
    }
}
