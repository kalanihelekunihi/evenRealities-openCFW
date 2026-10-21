#include <stdint.h>
#include <stddef.h>

extern int32_t osMessageQueueGet(void *,void *,uint8_t *,uint32_t);
extern void vPortFree(void *);
extern uint32_t r1_glasses_connection_handle_get(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern int32_t r1_native_ble_message_send(uint32_t,const void *,uint32_t,uint32_t,uint32_t);

const char r1_output_invalid_ring[] __attribute__((section(".r1.output.ring")))="[RING]glasses conn handle is invalid";
const char r1_output_invalid_sdk[] __attribute__((section(".r1.output.sdk")))="glasses conn handle is invalid";

int32_t r1_native_ble_send_phone(uint32_t id,const void *payload,uint32_t length)
{ return r1_native_ble_message_send(id,payload,length,1,200); }
int32_t r1_native_ble_send_glasses(uint32_t id,const void *payload,uint32_t length)
{ return r1_native_ble_message_send(id,payload,length,0,100); }

/* Byte reads express the consumed fields without C alignment assumptions.
 * MMU/bus fault granularity and original load instructions remain separate. */
static uint32_t read16(const volatile uint8_t *p)
{ return (uint32_t)p[0]|((uint32_t)p[1]<<8); }
static uint32_t read32(const volatile uint8_t *p)
{ return read16(p)|(read16(p+2)<<16); }
void r1_native_output_worker(void *context)
{
    for (;;) {
        uint8_t *volatile message=0;
        void *queue=*(void *volatile *)((uint8_t *)context+12);
        if (osMessageQueueGet(queue,(void *)&message,0,0)!=0 || !message) return;
        uint32_t type=read32(message+4);
        if (type==0 || type==2) {
            if (r1_glasses_connection_handle_get()!=0xffff) {
                uint8_t *current=message;
                uint32_t length=read16(current+8),id=read16(current);
                (void)r1_native_ble_send_glasses(id,current+12,length);
            } else {
                if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
                    r1_structured_log_format(0x04000000,r1_output_invalid_ring,r1_output_invalid_ring);
                if (r1_structured_log_mode_get()&2u)
                    nrf_log_frontend_std_0(0x001c0001,r1_output_invalid_sdk);
            }
        } else if (type==1) {
            uint8_t *current=message;
            uint32_t length=read16(current+8),id=read16(current);
            (void)r1_native_ble_send_phone(id,current+12,length);
        }
        vPortFree(message);
    }
}
