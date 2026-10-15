/* Apollo S200 Hongshi partial-refresh wrapper at 0x5bcd44. */
#include <stdint.h>

extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);
extern uint32_t display_driver_uled_qspi_write_async_59ce1e(const void *);

uint32_t display_driver_uled_type1_frame_lower_5bcd44(
        uint32_t x,uint32_t y,uint32_t a,uint32_t b,uint32_t width,uint32_t height) {
    (void)x;(void)y;(void)a;(void)b;
    /* The native routine clips its stack arguments, but copies a fixed
       descriptor template; the clipped values do not enter that descriptor. */
    if (width >= 640u) width=639u;
    if (height >= 480u) height=479u;
    (void)width;(void)height;
    uint32_t handle=*(volatile const uint32_t *)(uintptr_t)0x20074510u;
    if (handle==0u) {
        if ((g2_flashdb_candidate_flags()&2u)!=0u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x785c80u,
                (const char *)(uintptr_t)0x6ecca8u,
                (const char *)(uintptr_t)0x733614u,0x339u,
                (const char *)(uintptr_t)0x75f7d0u);
        if ((g2_flashdb_candidate_flags()&1u)!=0u ||
            (g2_flashdb_candidate_flags()&4u)!=0u)
            (void)audio_log_simple(0x04000000u,
                (const char *)(uintptr_t)0x73e424u,
                (const char *)(uintptr_t)0x73e424u);
        return UINT32_MAX;
    }
    uint8_t descriptor[28];
    const uint8_t *template=(const uint8_t *)(uintptr_t)0x76b164u;
    for (uint32_t i=0;i<28u;i++) descriptor[i]=template[i];
    uint32_t payload=*(volatile const uint32_t *)(uintptr_t)0x20074514u;
    for (uint32_t i=0;i<4u;i++) {
        descriptor[20u+i]=(uint8_t)(payload>>(8u*i));
        descriptor[24u+i]=(uint8_t)(handle>>(8u*i));
    }
    (void)display_driver_uled_qspi_write_async_59ce1e(descriptor);
    return 0u;
}
