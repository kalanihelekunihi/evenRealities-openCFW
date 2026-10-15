/* Apollo S200 NPMX watchdog kick at 0x5118e8. */
#include <stdint.h>

extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint32_t,const char *,const char *,
                                      const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

typedef uint32_t (*npmx_write_fn)(uint32_t, uint32_t, const uint8_t *,
                                   uint32_t);

static const char npmx_module[] = "npmx_driver";
static const char npmx_source_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\npmx_driver_transplant\\src\\npmx_main_driver.c";
static const char npmx_function[] = "npmx_watchdog_kick";
static const char npmx_error[] =
    "ERROR:kick npmx watchdog task_trigger=%d\n";
static const char npmx_compact_error[] =
    "[npmx_driver]ERROR:kick npmx watchdog task_trigger=%d\n";

uint32_t audio_ble_npmx_kick_watchdog_5118e8(uint32_t arg0,
                                               uint32_t arg1,
                                               uint32_t arg2,
                                               uint32_t arg3) {
    (void)arg2;
    (void)arg3;
    /* The device base is 0x20070f78; slot zero begins at +0x84. */
    const uint32_t slot = 0x20070f78u + 0x84u;
    const uint32_t driver = *(volatile const uint32_t *)(uintptr_t)slot;
    const uint32_t entry = *(volatile const uint32_t *)(uintptr_t)driver;
    const uint32_t context =
        *(volatile const uint32_t *)(uintptr_t)(driver + 8u);
    const uint8_t command = 1u;
    const uint32_t result = ((npmx_write_fn)(uintptr_t)entry)(
        context,0x704u,&command,1u);
    if (result == 0x2bad0000u) return arg0;
    if (g2_flashdb_candidate_flags() & 2u) {
        g2_flashdb_candidate_log(1u,
            npmx_module,npmx_source_path,npmx_function,0x242u,
            npmx_error,result,arg3);
        arg0 = 0x242u;
        arg1 = (uint32_t)(uintptr_t)npmx_error;
    }
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x04400000u,
            npmx_compact_error,npmx_compact_error,result);
    (void)arg1;
    return arg0;
}
