/* Stock 0x43ca50..0x43cb83: compact packet ring insertion and wakeup. */
#include <stdint.h>
extern volatile uint32_t g2_audio_log_ring_state[4]; /* 0x200004c8 */
extern void *audio_log_lock_state; /* pointer cell 0x20074388 */
extern int32_t audio_log_lock(void *,uint32_t);
extern void audio_log_unlock(void *);
extern uint32_t audio_log_flags(void);
extern void g2_lfs_memcpy(void *,const void *,uint32_t);
extern uint32_t audio_log_wake_allowed(void); /* stock 0x443484 */
extern uint32_t audio_log_transport_ready(void); /* stock 0x4487ac */
extern void audio_log_transport_wake(void); /* stock 0x448f7c */

void audio_log_emit(const void *packet,uint32_t length)
{
    uint32_t base=g2_audio_log_ring_state[0];
    uint32_t capacity=g2_audio_log_ring_state[1];
    uint32_t read=g2_audio_log_ring_state[2];
    uint32_t write=g2_audio_log_ring_state[3];
    uint32_t overflow=0;
    uint32_t ipsr;
    __asm volatile("mrs %0, ipsr" : "=r"(ipsr));
    void *lock=audio_log_lock_state;
    if (ipsr!=0u || lock==0) return;
    if (audio_log_lock(lock,500u)!=1) return;
    if (capacity>=read && capacity>=write) {
        uint32_t free_count;
        if (write<read) free_count=read-write-1u;
        else free_count=read+(capacity-write)-1u;
        if ((uint16_t)length>=free_count) {
            overflow=1u;
        } else {
            uint32_t until_end=capacity-write;
            uint32_t amount=(uint16_t)length;
            const uint8_t *source=(const uint8_t *)packet;
            if (until_end>=amount) {
                g2_lfs_memcpy((void *)(uintptr_t)(base+write),source,amount);
            } else {
                g2_lfs_memcpy((void *)(uintptr_t)(base+write),source,until_end);
                g2_lfs_memcpy((void *)(uintptr_t)base,source+until_end,amount-until_end);
            }
            if (amount>=until_end) write=amount-until_end;
            else write=(uint16_t)amount+write;
            g2_audio_log_ring_state[3]=write;
            if (audio_log_flags()&4u) {
                if (capacity-free_count>=236u) overflow=1u;
            } else if (audio_log_flags()&1u) {
                if (capacity-free_count>=4096u) overflow=1u;
            }
        }
    }
    audio_log_unlock(audio_log_lock_state);
    if ((uint8_t)overflow && (audio_log_flags()&1u)) {
        if (audio_log_wake_allowed()==0u || audio_log_transport_ready()==0u)
            audio_log_transport_wake();
    }
}
