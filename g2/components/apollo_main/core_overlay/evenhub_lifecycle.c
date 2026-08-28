/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded EvenHub lifecycle and IMU-state replacements for the Even
 * Realities G2 2.2.6.10 Apollo510B application. Exact stock boundaries,
 * callers, state addresses, and behavior are recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_EVENHUB_ACTIVE_WORD
#define OPEN_CFW_EVENHUB_ACTIVE_WORD \
    (*(volatile unsigned int *)0x200745C4U)
#endif

#ifndef OPEN_CFW_EVENHUB_STATE_WORD
#define OPEN_CFW_EVENHUB_STATE_WORD \
    (*(volatile unsigned int *)0x200745B8U)
#endif

#ifndef OPEN_CFW_EVENHUB_KEEPALIVE_WORD
#define OPEN_CFW_EVENHUB_KEEPALIVE_WORD \
    (*(volatile unsigned int *)0x200745ACU)
#endif

#ifndef OPEN_CFW_EVENHUB_SHUTDOWN_BYTE
#define OPEN_CFW_EVENHUB_SHUTDOWN_BYTE \
    (*(volatile unsigned char *)0x20074FC4U)
#endif

#ifndef OPEN_CFW_EVENHUB_IMU_ENABLED_WORD
#define OPEN_CFW_EVENHUB_IMU_ENABLED_WORD \
    (*(volatile unsigned int *)0x200745B4U)
#endif

#ifndef OPEN_CFW_EVENHUB_IMU_STATUS_WORD
#define OPEN_CFW_EVENHUB_IMU_STATUS_WORD \
    (*(volatile unsigned int *)0x200745C8U)
#endif

typedef void (*open_cfw_evenhub_imu_control_fn)(
    unsigned int report_frequency
);

#ifndef OPEN_CFW_EVENHUB_IMU_START
#define OPEN_CFW_EVENHUB_IMU_START(report_frequency) \
    (((open_cfw_evenhub_imu_control_fn)0x0054F381U)(report_frequency))
#endif

#ifndef OPEN_CFW_EVENHUB_IMU_STOP
#define OPEN_CFW_EVENHUB_IMU_STOP(report_frequency) \
    (((open_cfw_evenhub_imu_control_fn)0x0054F50FU)(report_frequency))
#endif

/*
 * Stock ABI: no arguments and no return value. Mark the shared EvenHub
 * lifecycle word active.
 */
__attribute__((used, noinline))
void open_cfw_evenhub_active_mark(void)
{
    OPEN_CFW_EVENHUB_ACTIVE_WORD = 1U;
}

/* Stock ABI: return the shared EvenHub state word in r0. */
__attribute__((used, noinline))
unsigned int open_cfw_evenhub_state_get(void)
{
    return OPEN_CFW_EVENHUB_STATE_WORD;
}

/* Stock ABI: store r0 to the shared EvenHub state word. */
__attribute__((used, noinline))
void open_cfw_evenhub_state_set(unsigned int state)
{
    OPEN_CFW_EVENHUB_STATE_WORD = state;
}

/* Stock ABI: reset the shared EvenHub keepalive word to zero. */
__attribute__((used, noinline))
void open_cfw_evenhub_keepalive_reset(void)
{
    OPEN_CFW_EVENHUB_KEEPALIVE_WORD = 0U;
}

/* Stock ABI: set the byte-wide EvenHub shutdown latch. */
__attribute__((used, noinline))
void open_cfw_evenhub_shutdown_mark(void)
{
    OPEN_CFW_EVENHUB_SHUTDOWN_BYTE = 1U;
}

/*
 * Stock ABI: r0 is the requested IMU enable value and r0 returns the shared
 * status word. Only an exact request of one starts an inactive stream; only
 * an exact request of zero stops a stream whose enable word is exactly one.
 * Both stock driver calls use report-frequency selector five.
 */
__attribute__((used, noinline))
unsigned int open_cfw_evenhub_imu_enable(unsigned int enabled)
{
    if (enabled == 1U && OPEN_CFW_EVENHUB_IMU_ENABLED_WORD == 0U) {
        OPEN_CFW_EVENHUB_IMU_ENABLED_WORD = 1U;
        OPEN_CFW_EVENHUB_IMU_START(5U);
    } else if (
        enabled == 0U &&
        OPEN_CFW_EVENHUB_IMU_ENABLED_WORD == 1U
    ) {
        OPEN_CFW_EVENHUB_IMU_ENABLED_WORD = 0U;
        OPEN_CFW_EVENHUB_IMU_STOP(5U);
    }

    return OPEN_CFW_EVENHUB_IMU_STATUS_WORD;
}
