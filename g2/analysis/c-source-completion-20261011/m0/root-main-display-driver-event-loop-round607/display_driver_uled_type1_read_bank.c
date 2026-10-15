/* Apollo S200 Hongshi bank read with three-attempt retry at 0x5bbe80. */
#include <stdint.h>

extern uint32_t display_driver_uled_type1_read_register_5bbe3e(uint32_t,
                                                                 uint32_t *,uint32_t,uint32_t);
extern uint32_t display_driver_uled_delay_449376(uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_type1_read_bank_5bbe80(uint32_t bank,
                                                      uint32_t mode) {
    uint32_t word=0u,attempts=0u,result;
    do {
        result=display_driver_uled_type1_read_register_5bbe3e(
            (uint8_t)bank,&word,1u,(uint8_t)mode);
        if (result==0u) break;
        attempts=(uint8_t)(attempts+1u);
        if ((g2_flashdb_candidate_flags()&2u)!=0u)
            g2_flashdb_candidate_log(2u,(const char *)(uintptr_t)0x785c80u,
                (const char *)(uintptr_t)0x6ecca8u,
                (const char *)(uintptr_t)0x753b34u,0x140u,
                (const char *)(uintptr_t)0x70af64u,attempts,result);
        if ((g2_flashdb_candidate_flags()&1u)!=0u ||
            (g2_flashdb_candidate_flags()&4u)!=0u)
            (void)audio_log_simple(0x08800000u,
                (const char *)(uintptr_t)0x6eccf8u,
                (const char *)(uintptr_t)0x6eccf8u,attempts,result);
        (void)display_driver_uled_delay_449376(2u);
    } while (attempts<3u);
    if (attempts==3u) {
        if ((g2_flashdb_candidate_flags()&2u)!=0u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x785c80u,
                (const char *)(uintptr_t)0x6ecca8u,
                (const char *)(uintptr_t)0x753b34u,0x148u,
                (const char *)(uintptr_t)0x71465cu,attempts);
        if ((g2_flashdb_candidate_flags()&1u)!=0u ||
            (g2_flashdb_candidate_flags()&4u)!=0u)
            (void)audio_log_simple(0x04400000u,
                (const char *)(uintptr_t)0x6f9d94u,
                (const char *)(uintptr_t)0x6f9d94u,attempts);
        return 0xffu;
    }
    if ((g2_flashdb_candidate_flags()&2u)!=0u)
        g2_flashdb_candidate_log(4u,(const char *)(uintptr_t)0x785c80u,
            (const char *)(uintptr_t)0x6ecca8u,
            (const char *)(uintptr_t)0x753b34u,0x150u,
            (const char *)(uintptr_t)0x6f9ddcu,result,
            (word>>24)&0xffu,(word>>16)&0xffu,(word>>8)&0xffu,word&0xffu);
    if ((g2_flashdb_candidate_flags()&1u)!=0u ||
        (g2_flashdb_candidate_flags()&4u)!=0u)
        (void)audio_log_simple(0x11400000u,
            (const char *)(uintptr_t)0x6e2fe8u,
            (const char *)(uintptr_t)0x6e2fe8u,result,
            (word>>24)&0xffu,(word>>16)&0xffu,(word>>8)&0xffu,word&0xffu);
    return word&0xffu;
}
