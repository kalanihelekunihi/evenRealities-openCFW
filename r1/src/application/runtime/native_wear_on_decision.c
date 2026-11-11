#include <stdint.h>
#include "../board/native_battery_memory.h"

extern volatile uint8_t r1_wear_adt_history[20],r1_wear_adt_active,r1_health_mode_byte;
extern volatile uint32_t r1_wear_adt_stream,r1_wear_adt_count;
extern uint32_t r1_wear_optical_history_range(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);

static uint32_t latest_history(void)
{
    uintptr_t address=(uintptr_t)r1_wear_adt_history+(uint32_t)r1_wear_adt_active*4u-4u;
    return read32((const volatile uint8_t *)address);
}

/* GCC strict FP preserves the native signaling comparison and FPSCR. */
__attribute__((noinline,noclone)) static int variance_above(float value)
{
    return value > 2000.0f;
}

void r1_wear_on_decision(void *statistics)
{
    if (r1_wear_adt_stream && r1_wear_adt_active) {
        uint32_t range=r1_wear_optical_history_range();
        if (r1_wear_adt_count && range<100000u) {
            if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
                (void)r1_structured_log_format(0x0c400000,
                    "[RING]algo wear ir-data-range %d","[RING]algo wear ir-data-range %d",range);
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_1(0x001c0003,"algo wear ir-data-range %d",range);
            return;
        }
        if (latest_history()<=UINT32_C(0x8a1790)) return;
        r1_health_mode_byte=1;
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
            uint32_t latest=latest_history();
            (void)r1_structured_log_format(0x0c400000,
                "[RING]algo wear ir-sus-on: %d","[RING]algo wear ir-sus-on: %d",latest);
        }
        if (r1_structured_log_mode_get()&2u) {
            uint32_t latest=latest_history();
            nrf_log_frontend_std_1(0x001c0003,"algo wear ir-sus-on: %d",latest);
        }
        return;
    }
    volatile float *values=(volatile float *)statistics;
    if (variance_above(values[3]) || variance_above(values[4]) || variance_above(values[5])) {
        r1_health_mode_byte=1;
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x0c000000,
                "[RING]algo wear active-sus-on","[RING]algo wear active-sus-on");
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_0(0x001c0003,"algo wear active-sus-on");
    }
}
