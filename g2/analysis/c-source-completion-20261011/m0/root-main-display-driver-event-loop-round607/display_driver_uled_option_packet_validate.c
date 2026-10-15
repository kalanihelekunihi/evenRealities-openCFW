/* Apollo S200 packet descriptor validator at 0x59cb42. */
#include <stdint.h>

extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_packet_validate_59cb42(const void *packet,
                                                      const char *caller) {
    uint32_t line;
    const char *detail;
    if (packet == 0) {
        line=0x98u;
        detail=(const char *)(uintptr_t)0x76b2d0u;
    } else if (((const uint32_t *)packet)[6] == 0u) {
        line=0x9du;
        detail=(const char *)(uintptr_t)0x75f8f0u;
    } else if (((const uint32_t *)packet)[5] == 0u) {
        line=0xa2u;
        detail=(const char *)(uintptr_t)0x76b2ecu;
    } else {
        return 0u;
    }
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
            (const char *)(uintptr_t)0x6f9fd4u,
            (const char *)(uintptr_t)0x776e2cu,line,detail,caller);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u)) {
        const char *short_detail=line==0x98u
            ? (const char *)(uintptr_t)0x733794u
            : line==0x9du ? (const char *)(uintptr_t)0x729078u
                            : (const char *)(uintptr_t)0x7337c4u;
        (void)audio_log_simple(0x04400000u,short_detail,short_detail,caller);
    }
    return UINT32_MAX;
}
