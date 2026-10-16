#include "native_stacmd.h"
#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
const char r1_stacmd_write_retry_ring[] __attribute__((section(".r1.stacmd_retry.ring")))="[RING]write failed--retry number=%d\r\n";
const char r1_stacmd_write_retry_sdk[] __attribute__((section(".r1.stacmd_retry.sdk")))="write failed--retry number=%d\r\n";
uint32_t r1_stacmd_write_retry_native(uint32_t reg,uint32_t length,const uint8_t *bytes)
{
    for (uint32_t attempt=1;attempt<10;attempt++) {
        r1_stacmd_bus_recovery_native();
        uint32_t result=r1_stacmd_write_frame_native(0x44,reg,length,bytes);
        if (result) return result;
        if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x0c400000,r1_stacmd_write_retry_ring,r1_stacmd_write_retry_ring,attempt);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0003,r1_stacmd_write_retry_sdk,attempt);
        r1_stacmd_failed_transactions=r1_stacmd_failed_transactions+1;
    }
    return 0;
}
