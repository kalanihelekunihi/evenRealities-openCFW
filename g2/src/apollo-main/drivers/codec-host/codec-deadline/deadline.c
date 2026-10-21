/* Reconstructed one-byte codec deadline helper0x58FAD2; fixture scheduler only. */
#include "deadline.h"
extern uint64_t codec_tick64(void);
extern uint32_t codec_uart_read(uint8_t *,uint32_t);
extern uint32_t codec_delay_tick(uint32_t);
uint32_t codec_read_byte_deadline(uint8_t *dst,uint32_t timeout){
    uint64_t start=codec_tick64(),now=start;
    uint64_t deadline=start+(uint64_t)(int64_t)(int32_t)timeout;
    for(;;){
        if(deadline<=now)return UINT32_MAX;
        if(codec_uart_read(dst,1)==1)return 1;
        codec_delay_tick(1);now=codec_tick64();
    }
}
