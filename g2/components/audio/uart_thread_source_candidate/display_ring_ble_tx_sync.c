/* Native threadBleWsfTakeTxReady 0x4d0b36, wait 0x4d0b64, and
 * thread_ble_wsf_tx_complete_notify 0x4d0c36. The thread state is live
 * RAM 0x20004068, with the semaphore handle at offset 0x14. */
#include <stdint.h>
extern uint8_t audio_ble_wsf_thread_state[];
extern uint32_t g2_flashdb_candidate_tick(void); /* selected osKernelGetTickCount */
extern uint32_t audio_delay(uint32_t); /* selected osDelay */
extern int32_t audio_semaphore_acquire(void *,uint32_t); /* selected osSemaphoreAcquire */
extern int32_t audio_semaphore_release(void *); /* selected osSemaphoreRelease */
extern uint32_t audio_semaphore_get_count(void *); /* native osSemaphoreGetCount */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="task.ble.wsf";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ble_wsf.c";
static const char wait_fn[]="thread_ble_wsf_wait_tx_ready";
static const char notify_fn[]="thread_ble_wsf_tx_complete_notify";
static const char timeout[]="wait_tx_ready count >= 20(400ms), break";
static const char timeout_short[]="[task.ble.wsf]wait_tx_ready count >= 20(400ms), break";
static const char success[]="wait_tx_ready success, time = %d ms, count = %d";
static const char success_short[]="[task.ble.wsf]wait_tx_ready success, time = %d ms, count = %d";
static const char release_error[]="Failed to release semaphore, status: %d, count: %d";
static const char release_error_short[]="[task.ble.wsf]Failed to release semaphore, status: %d, count: %d";
static const char already[]="tx_complete_notify: semaphore already at max count (%d), skipping release";
static const char already_short[]="[task.ble.wsf]tx_complete_notify: semaphore already at max count (%d), skipping release";
static void *tx_semaphore(void) {
    return *(void **)(void *)(audio_ble_wsf_thread_state+0x14u);
}
uint32_t audio_ble_take_tx_ready(uint32_t timeout_ticks) {
    void *sem=tx_semaphore();
    return sem!=0 && audio_semaphore_acquire(sem,(uint16_t)timeout_ticks)==0;
}
void audio_ble_tx_ready_wait(void) {
    uint32_t start=g2_flashdb_candidate_tick();
    uint8_t count=0u;
    uint32_t acquired=audio_ble_take_tx_ready(0u);
    if(acquired==0u) {
        uint32_t timed_out=1u;
        do {
            if(acquired!=0u){timed_out=0u;break;}
            acquired=audio_ble_take_tx_ready(10u);
            if(acquired==0u)(void)audio_delay(10u);
            count=(uint8_t)(count+1u);
        } while(count<20u);
        if(timed_out!=0u) {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(2u,module,path,wait_fn,211u,timeout);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x08000000u,timeout_short,timeout_short);
        }
    }
    uint32_t elapsed=g2_flashdb_candidate_tick()-start;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,wait_fn,217u,success,elapsed,count);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,success_short,success_short,elapsed,count);
}
void audio_ble_tx_complete_notify(void) {
    void *sem=tx_semaphore();
    if(sem==0)return;
    uint32_t count=audio_semaphore_get_count(sem);
    if(count==0u) {
        int32_t status=audio_semaphore_release(sem);
        if(status!=0) {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(2u,module,path,notify_fn,242u,release_error,status,0);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x08800000u,release_error_short,release_error_short,status,0);
        }
    } else {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,notify_fn,245u,already,count);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10400000u,already_short,already_short,count);
    }
}
