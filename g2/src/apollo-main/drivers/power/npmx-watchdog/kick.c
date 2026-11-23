/* Apollo S200 NPMX watchdog kick at 0x5118e8. */
#include <stdint.h>

/* Sim-test fix (2026-10-26): stock literal 0x20070f78 is the npmx_instance
 * that npmx_main_driver.c defines as g2_npmx_instance; our link places it
 * elsewhere, so the literal read zero (Renode HardFault blx 0 in the kick). */
struct npmx_instance;
extern struct npmx_instance g2_npmx_instance; /* RAM 0x20070f78 */

extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint32_t,const char *,const char *,
                                      const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

extern void *npmx_timer_get(struct npmx_instance *p_pm, uint8_t idx);     /* stock 0x55ef6c */
extern uint32_t npmx_timer_task_trigger(void *p_timer, uint32_t task);    /* stock 0x55ef76 */

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
    /* Stock 0x5118e8 makes two direct calls (not an indirect fn-ptr write):
     *   timer  = npmx_timer_get(&g2_npmx_instance, 0);   (r1=#0 then bl 0x55ef6c)
     *   result = npmx_timer_task_trigger(timer, 3);       (r1=#3 then bl 0x55ef76) */
    void *timer = npmx_timer_get(&g2_npmx_instance, 0u);
    const uint32_t result = npmx_timer_task_trigger(timer, 3u);
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
