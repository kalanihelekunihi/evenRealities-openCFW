/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Onboarding-state gate replacement for the Even Realities G2 2.2.6.10
 * Apollo510B application. Exact stock boundaries, callers, fixed ABI, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

typedef unsigned int (*open_cfw_ui_onboarding_state_fn)(void);

#ifndef OPEN_CFW_UI_ONBOARDING_STATE_PRIMARY
#define OPEN_CFW_UI_ONBOARDING_STATE_PRIMARY \
    ((open_cfw_ui_onboarding_state_fn)0x00467F09U)
#endif

#ifndef OPEN_CFW_UI_ONBOARDING_STATE_SECONDARY
#define OPEN_CFW_UI_ONBOARDING_STATE_SECONDARY \
    ((open_cfw_ui_onboarding_state_fn)0x00468035U)
#endif

#ifndef OPEN_CFW_UI_ONBOARDING_STATE_TERTIARY
#define OPEN_CFW_UI_ONBOARDING_STATE_TERTIARY \
    ((open_cfw_ui_onboarding_state_fn)0x00469AE3U)
#endif

/*
 * Stock ABI at 0x00442D64:
 *   no arguments; r0 is one when any onboarding state is exactly one.
 *
 * The three queries are ordered and short-circuited. Noncanonical nonzero
 * values do not count as active.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_onboarding_running(void)
{
    if (OPEN_CFW_UI_ONBOARDING_STATE_PRIMARY() == 1U) {
        return 1U;
    }
    if (OPEN_CFW_UI_ONBOARDING_STATE_SECONDARY() == 1U) {
        return 1U;
    }
    if (OPEN_CFW_UI_ONBOARDING_STATE_TERTIARY() == 1U) {
        return 1U;
    }
    return 0U;
}
