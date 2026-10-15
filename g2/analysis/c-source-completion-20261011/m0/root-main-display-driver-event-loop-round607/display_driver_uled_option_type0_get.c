/* Apollo S200 type-0 option register getter at 0x592f9a. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t display_driver_uled_type0_read_59275e(uint32_t,void *,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_type0_get_592f9a(uint16_t *value) {
    uint8_t reply[36];
    audio_uart_buffer_zero(reply,36u,0u);
    uint32_t status=display_driver_uled_type0_read_59275e(0x9fu,reply,4u);
    if (status != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(2u,(const char *)(uintptr_t)0x785c90u,
                (const char *)(uintptr_t)0x6f313cu,
                (const char *)(uintptr_t)0x753c9cu,0x256u,
                (const char *)(uintptr_t)0x749894u,status);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x08400000u,
                (const char *)(uintptr_t)0x71e338u,
                (const char *)(uintptr_t)0x71e338u,status);
        return UINT32_MAX;
    }
    uint32_t result=((uint32_t)reply[1]<<8) | reply[2];
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(3u,(const char *)(uintptr_t)0x785c90u,
            (const char *)(uintptr_t)0x6f313cu,
            (const char *)(uintptr_t)0x753c9cu,0x259u,
            (const char *)(uintptr_t)0x76b1d4u,result);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x0c400000u,
            (const char *)(uintptr_t)0x73e500u,
            (const char *)(uintptr_t)0x73e500u,result);
    if (value != 0) *value=(uint16_t)result;
    return 0u;
}
