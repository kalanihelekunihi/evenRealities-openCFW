/* Independent reconstruction of target Thumb function 0xa1c0. Offline only. */
#include "pm.h"
#define PREVENT (*(volatile uint8_t *)0x20000f1du)
#define MEASURING (*(volatile uint8_t *)0x20000f1eu)
uint32_t touch_ilo_deep_sleep_callback(void *params, uint32_t mode)
{
    (void)params;
    switch (mode) {
    case 1: /* CHECK_READY */
        if (MEASURING) return 0x4200ffu;
        PREVENT = 1;
        return 0;
    case 2: /* CHECK_FAIL */
    case 8: /* AFTER_TRANSITION */
        PREVENT = 0;
        return 0;
    case 4: /* BEFORE_TRANSITION: no EXCO/WCO code in this target */
        return 0;
    default:
        return 0x4200ffu;
    }
}
