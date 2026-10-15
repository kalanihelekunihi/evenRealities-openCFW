/* Apollo S200 brightness snapshot at 0x46c410. */
#include <stdint.h>

extern uint32_t display_driver_brightness_max_lum_46c23c(void);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

void display_driver_uled_type0_context_snapshot_46c410(uint32_t requested,
                                                         uint32_t *first,
                                                         uint32_t *second) {
    uint32_t level=requested;
    if (level>=101u) level=100u;
    else if (level<2u) level=2u;
    uint32_t maximum=display_driver_brightness_max_lum_46c23c();
    uint32_t value;
    uint32_t line,detail,short_detail;
    if (level<31u) {
        *first=0u;
        value=((maximum-333u)*(level-2u)+14u)/28u+333u;
        *second=value;
        line=0x223u;detail=0x72d8c8u;short_detail=0x705c88u;
    } else {
        value=(36u*level-0x415u)/70u;
        *first=value;
        *second=maximum;
        line=0x22du;detail=0x72d8fcu;short_detail=0x705cccu;
    }
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(3u,(const char *)(uintptr_t)0x7835b4u,
            (const char *)(uintptr_t)0x6e9ee0u,
            (const char *)(uintptr_t)0x7437acu,line,
            (const char *)(uintptr_t)detail,level,value,maximum);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x0cc00000u,
            (const char *)(uintptr_t)short_detail,
            (const char *)(uintptr_t)short_detail,level,value,maximum);
}
