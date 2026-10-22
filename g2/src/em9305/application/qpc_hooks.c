/* EM9305 product QP/C hook providers installed in the QF callback slots
 * (startup 0x80fe10/0x80fe0c, resume 0x80fe08/0x80fe04, idle 0x80fe18/0x80fe14).
 * Native veneers 0x3100ec, 0x310728, 0x311150, 0x3111a4 and the idle shell
 * 0x311620..0x311634. All are tail branches or short call shells.
 */
#include <stdint.h>

extern void wsfOsRunIdleTasks(void);                      /* 0x333d7c */
extern void volt_monitor_measure_zero_3119a8(void);       /* VoltMon_DoMeasurement(0) veneer */
extern uint32_t opencfw_em9305_pal_hook_two(uint32_t value);  /* 0x3101e8 */
extern uint32_t opencfw_em9305_pal_resume_dispatch(void); /* PalUartResume 0x310798 */
extern void application_startup_hook_30482c(void);

/* Stock 0x003100EC (TSV name VoltMon_DoMeasurement; renamed because the EM SDK
 * function of that name (pml_volt_monitor.c.obj) is the final target). */
void volt_monitor_idle_veneer_3100ec(void)
{
    volt_monitor_measure_zero_3119a8();
}

/* Stock 0x00310728 (idle_final_noop: R0 = 16, tail to an empty PAL hook) */
uint32_t idle_final_noop(void)
{
    return opencfw_em9305_pal_hook_two(16u);
}

/* Stock 0x00311150 (QF_onResumeInternalHook: tail to PalUartResume) */
uint32_t QF_onResumeInternalHook(void)
{
    return opencfw_em9305_pal_resume_dispatch();
}

/* Stock 0x003111A4 (qf_on_startup_internal_hook: tail to the product startup hook) */
void qf_on_startup_internal_hook(void)
{
    application_startup_hook_30482c();
}

/* Stock 0x00311620 (QK_onIdleInternalHook). Stock passes R0 = 0 to the final
 * veneer, which overwrites it; the hook returns that veneer's R0. */
uint32_t QK_onIdleInternalHook(void)
{
    wsfOsRunIdleTasks();
    volt_monitor_idle_veneer_3100ec();
    return idle_final_noop();
}
