#include <stdint.h>

extern uint32_t case_write_controller_blocking(void *uart,const uint8_t *byte,uint32_t length,uint32_t timeout);
extern int32_t g2_log_printf(const char *format,...);
extern void log_hex_buffer(const uint8_t *bytes,uint32_t length);

/* Original 0x0800680c. Lower UART write and logging contracts are explicit.
 * Valid input is a readable payload of length at most 65535 bytes. */
/* Stock 0x0800680C (case_send) */
void case_send(const uint8_t *payload,uint32_t length)
{
    uint8_t byte;
    uint8_t checksum=(uint8_t)(length-2u);
    void *uart=(void *)(uintptr_t)0x20000e24u;
    const uint32_t timeout=0xffffu;
    byte=0x5au;(void)case_write_controller_blocking(uart,&byte,1u,timeout);
    byte=0xa5u;(void)case_write_controller_blocking(uart,&byte,1u,timeout);
    byte=0xffu;(void)case_write_controller_blocking(uart,&byte,1u,timeout);
    byte=(uint8_t)length;(void)case_write_controller_blocking(uart,&byte,1u,timeout);
    for(uint16_t i=0;i<length;i++){
        byte=payload[i];
        (void)case_write_controller_blocking(uart,&byte,1u,timeout);
        checksum=(uint8_t)(checksum+payload[i]);
    }
    byte=checksum;(void)case_write_controller_blocking(uart,&byte,1u,timeout);
    if(*(volatile uint8_t *)(uintptr_t)0x20000895u==0u){
        if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u)
            g2_log_printf("\n(**%02x**:",checksum);
        log_hex_buffer(payload,length);
    }
}
