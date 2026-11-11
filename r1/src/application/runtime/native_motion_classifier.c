#include <stdint.h>
#include "native_float_to_signed.h"
#include "../board/native_battery_memory.h"

extern volatile uint8_t r1_motion_detection_state[48];
volatile uintptr_t r1_motion_detection_callback __attribute__((section(".r1.motion.detection.callback"),aligned(4)))=0;
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
static int32_t signed_bits(float value)
{union {float f;int32_t i;} x={.f=value};return x.i;}
static uint32_t scaled_bits(float value)
{
    /* Executed once on a changed state, even when both log paths are off. */
    return r1_native_float_to_signed32(value*1000.0f);
}
void r1_native_motion_detection_classify(float value)
{
    volatile uint8_t *state=r1_motion_detection_state;
    if (read16(state+34)<8) return;
    int32_t raw=signed_bits(value);
    uint32_t previous=state[38];
    if (raw>INT32_C(0x3d4ccccd)) {
        write16(state+36,0);state[38]=0;
    } else {
        uint32_t count=read16(state+36);
        /* Keep the stock constant ordering, including its unreachable middle. */
        if (raw<INT32_C(0x3e051eb8)) {
            count=(uint16_t)(count+1u);write16(state+36,count);
            if (count>=600) state[38]=1;
        } else {
            if (count) {count=(uint16_t)(count-1u);write16(state+36,count);}
            if (!count) state[38]=0;
        }
    }
    if (!r1_motion_detection_callback) return;
    if (state[38]!=previous) {
        uint32_t first_mode=r1_structured_log_mode_get();
        uint32_t scaled=scaled_bits(value);
        if ((first_mode&1u)||(r1_structured_log_mode_get()&4u)) {
            uint32_t flag=state[38],count=read16(state+36);
            (void)r1_structured_log_format(0x0cc00000,
                "[RING]detect state changed: raw=%d cnt=%d static=%d",
                "[RING]detect state changed: raw=%d cnt=%d static=%d",scaled,count,flag);
        }
        if (r1_structured_log_mode_get()&2u) {
            uint32_t flag=state[38],count=read16(state+36);
            nrf_log_frontend_std_3(0x001c0003,"detect state changed: raw=%d cnt=%d static=%d",scaled,count,flag);
        }
    }
    uint32_t flag=state[38];
    uintptr_t callback=r1_motion_detection_callback;
    ((void (*)(uint32_t))callback)(flag);
}
