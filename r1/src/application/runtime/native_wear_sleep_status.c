#include <stdint.h>

/* Separate authenticated bytes; surrounding wear control is not owned here. */
volatile uint8_t r1_wear_sleep_status
    __attribute__((section(".r1.wear.sleep.status")))=0;
volatile uint8_t r1_wear_sleep_latch
    __attribute__((section(".r1.wear.sleep.latch")))=0;
/* Stock 0x4c6c0 reads the latch at wear-state base + 2. */
uint32_t r1_sleep_config_flag_get(void)
{
    return r1_wear_sleep_latch;
}
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);

void r1_wear_sleep_status_topic_callback(const volatile void *payload)
{
    uint32_t status=*(const volatile uint8_t *)payload;
    if (status==1 && !r1_wear_sleep_status) r1_wear_sleep_latch=0;
    r1_wear_sleep_status=(uint8_t)status;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t current=r1_wear_sleep_status;
        (void)r1_structured_log_format(0x0c400000,
            "[RING]algo wear sleep status change: %d",
            "[RING]algo wear sleep status change: %d",current);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t current=r1_wear_sleep_status;
        nrf_log_frontend_std_1(0x001c0003,"algo wear sleep status change: %d",current);
    }
}
