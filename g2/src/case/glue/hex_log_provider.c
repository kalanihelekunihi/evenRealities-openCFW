#include <stdint.h>

extern int32_t g2_log_printf(const char *format,...);

/* Original 0x080067c8. Valid input is a readable byte buffer of length
 * at most 65535. The logger-disable flag is rechecked for every byte and
 * before the final CRLF, because logging can change it between calls. */
/* Stock 0x080067C8 (log_hex_buffer) */
void log_hex_buffer(const uint8_t *bytes,uint32_t length)
{
    volatile uint8_t *disabled=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if(*disabled!=0u)return;
    for(uint16_t i=0;i<length;i++){
        if(*disabled==0u)g2_log_printf("%02x ",bytes[i]);
    }
    if(*disabled==0u)g2_log_printf("\r\n");
}
