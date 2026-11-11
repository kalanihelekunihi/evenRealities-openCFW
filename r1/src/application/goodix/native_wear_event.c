/* Stock R1 0x2eb84: wear-event routing, not the vendor demo notification. */
#include <stdint.h>
#include "native_wear_event.h"
#include "native_stream_callbacks.h"
#include "gh_drv.h"

extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void GhMultSensorWearEventSend(uint32_t);
extern void Gh3x2xDemoStopSampling(uint32_t);

_Static_assert(GH3X2X_IRQ_MSK_WEAR_OFF_BIT==0x800 &&
               GH3X2X_IRQ_MSK_WEAR_ON_BIT==0x400 &&
               GH3X2X_EVENT_EX_BIT_WEAR_LIVING_TYPE==1,
               "native wear bits");

__attribute__((always_inline)) static inline void r1_wear_log(const char *ring,
                                                               const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u) ||
        (r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000u,ring,ring);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_0(0x001c0003u,sdk);
}

void Gh3x2x_WearEventHook(uint16_t event,uint8_t extra)
{
    uintptr_t callbacks=(uintptr_t)r1_goodix_stream_callbacks;
    uint32_t callback;
    if (event&GH3X2X_IRQ_MSK_WEAR_OFF_BIT) {
        if (extra&GH3X2X_EVENT_EX_BIT_WEAR_LIVING_TYPE) {
            r1_wear_log("[RING]Wear off, no living-object!!!\r\n",
                        "Wear off, no living-object!!!\r\n");
            callback=((volatile uint32_t *)callbacks)[3];
            if (callback) (void)((uint32_t (*)(uint32_t))(uintptr_t)callback)(0);
            return;
        }
        r1_wear_log("[RING]Wear off, no object!!!\r\n",
                    "Wear off, no object!!!\r\n");
        callback=((volatile uint32_t *)callbacks)[3];
        if (callback) (void)((uint32_t (*)(uint32_t))(uintptr_t)callback)(0);
        GhMultSensorWearEventSend(2);
        return;
    }
    if (event&GH3X2X_IRQ_MSK_WEAR_ON_BIT) {
        if (extra&GH3X2X_EVENT_EX_BIT_WEAR_LIVING_TYPE) {
            r1_wear_log("[RING]Wear on, living-object!!!\r\n",
                        "Wear on, living-object!!!\r\n");
            callback=((volatile uint32_t *)callbacks)[3];
            if (callback) (void)((uint32_t (*)(uint32_t))(uintptr_t)callback)(1);
            Gh3x2xDemoStopSampling(0x200);
            return;
        }
        r1_wear_log("[RING]Wear on, object !!!\r\n",
                    "Wear on, object !!!\r\n");
        GhMultSensorWearEventSend(1);
    }
}
