#include <stdint.h>
extern uint32_t r1_glasses_connection_handle_get(void),r1_phone_connection_handle_get(void);
extern int32_t osSemaphoreAcquire(void *,uint32_t),osSemaphoreRelease(void *);
extern uint32_t osSemaphoreGetCount(void *);
extern void r1_adc_error(uint32_t);
extern unsigned char r1_native_bae8_service[];
extern uint32_t r1_native_bae8_send(void *,const void *,volatile uint32_t *,uint32_t,uint32_t);
void *volatile r1_ble_link_semaphores[2]
 __attribute__((section(".r1.ble.semaphores"),aligned(4)));

uint32_t r1_ble_error_is_benign(uint32_t status)
{ return status==0 || status==1 || status==5 || status==8 || status==19 || status==0x3002 || status==0x3401; }
void r1_ble_flush_bounded(void *semaphore,uint32_t count)
{
    if (!semaphore) return;
    for (uint32_t i=0;i<count;i++) {
        if (osSemaphoreGetCount(semaphore)>=4) return;
        (void)osSemaphoreRelease(semaphore);
    }
}
void r1_ble_flush_one(void *semaphore) { r1_ble_flush_bounded(semaphore,1); }
void r1_ble_flush_drain(void *semaphore)
{
    if (!semaphore) return;
    while (osSemaphoreAcquire(semaphore,0)==0) {}
    r1_ble_flush_bounded(semaphore,4);
}
void *r1_ble_link_semaphore(uint32_t connection)
{
    if (r1_glasses_connection_handle_get()==connection) return r1_ble_link_semaphores[0];
    if (r1_phone_connection_handle_get()==connection) return r1_ble_link_semaphores[1];
    return 0;
}
uint32_t r1_ble_semaphore_take(void *semaphore,uint32_t timeout)
{ return semaphore && osSemaphoreAcquire(semaphore,timeout)==0; }

/* The mutable length word is retained across the sole status-19 retry.
 * Semaphore ownership and error logging intentionally follow the stock paths,
 * including the zero-flag timeout bypass and repeated releases on errors. */
int32_t r1_native_ble_message_send(uint32_t connection,const void *payload,uint32_t length,uint32_t flag,uint32_t timeout)
{
    volatile uint32_t remaining=length;
    void *semaphore=r1_ble_link_semaphore(connection);
    uint32_t acquired=r1_ble_semaphore_take(semaphore,timeout),status;
    if (!flag) {
        status=r1_native_bae8_send(r1_native_bae8_service,payload,&remaining,connection,flag);
        if (!r1_ble_error_is_benign(status)) {
            if (!acquired) { r1_adc_error(status);return (int32_t)status; }
            r1_ble_flush_one(semaphore);r1_adc_error(status);
        }
        if (acquired && status) r1_ble_flush_one(semaphore);
        return (int32_t)status;
    }
    if (!acquired) return 19;
    status=r1_native_bae8_send(r1_native_bae8_service,payload,&remaining,connection,flag);
    if (!r1_ble_error_is_benign(status)) { r1_ble_flush_one(semaphore);r1_adc_error(status); }
    if (!status) return 0;
    if (status==19) {
        r1_ble_flush_one(semaphore);
        if (!r1_ble_semaphore_take(semaphore,1000)) return 19;
        status=r1_native_bae8_send(r1_native_bae8_service,payload,&remaining,connection,flag);
        if (!r1_ble_error_is_benign(status)) { r1_ble_flush_one(semaphore);r1_adc_error(status); }
    }
    if (status) r1_ble_flush_one(semaphore);
    return (int32_t)status;
}
