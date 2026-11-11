// SPDX-License-Identifier: Apache-2.0
/*
 * openCFW self-recovery arming primitive and crash-loop gate.
 *
 * NOT stock firmware. Added 2026-11-01 for the bricked-temple recovery work
 * (see g2/docs/reference/self-recovery-arming.md and
 * g2/docs/hardware-test-plan.md). The right G2 temple hangs before its app
 * comes up, so neither the BLE OTA receiver nor the case pogo product-test
 * path (both application services) can reach it; the only documented way into
 * a dead temple is the Apollo secure bootloader (SBL) wired-recovery path.
 *
 * Arming mirrors am_hal_mram_recovery_init_app_recovery(key, bReset=false)
 * (third-party/upstream/ambiqhal-apollo510/mcu/apollo510/hal/mcu/
 * am_hal_mram_recovery.c): write the recovery key to MCUCTRL->OTAPOINTER so
 * the SBL comes up in wired-load mode on the NEXT reset. No reset is forced
 * here (bReset=false): a healthy app keeps running; only a subsequent reset
 * enters recovery.
 *
 * Registers (Apollo510, cross-checked against our own MCUCTRL pokes in
 * hal/a-03-sysctrl/am_hal_sysctrl_sleep_variant.c and the Ambiq CMSIS header
 * apollo510.h, where OTAPOINTER is at struct offset 0x264):
 *   MCUCTRL base        0x40020000
 *   MCUCTRL->CHIPREV    0x4002000c  [7:0]: 0x22 = B1, 0x23 = B2 (B0 is < 0x22)
 *   MCUCTRL->OTAPOINTER 0x40020264  ("reset only by POA")
 * The upstream HAL refuses on APOLLO5_B0; we mirror that (arm only on >= B1).
 *
 * ---------------------------------------------------------------------------
 * NOT WIRED INTO THE BOOT PATH. g2_self_recovery_boot_check() below is a
 * complete, reviewable crash-loop gate, but it is intentionally NOT called
 * from board_init_5cdd14() yet. Arming drops the temple into an SBL wired-load
 * state on the next reset; the 2026-10-31 probe campaign found the case pogo
 * wired link silent, so that state may be unreachable on this hardware, and
 * the reset-cause the bricked right temple actually cycles through was never
 * captured. Wiring this to the wrong reset signal could strand the only
 * working (left) temple in an unreachable loader. Wire it only after the
 * brick's reset signature is recorded (crash_record / g2_reset_status) and the
 * wired path is confirmed reachable from an armed SBL. Until then the mechanism
 * exists and builds, and the left temple's safe rollback stays BLE OTA.
 * ---------------------------------------------------------------------------
 */
#include <stdint.h>
#include <stdbool.h>

uint32_t g2_mram_recovery_arm(void);
void g2_self_recovery_boot_check(bool wdt_reset, bool clean_reset);
void g2_self_recovery_mark_healthy(void);
void g2_recovery_arm_early(void);
void g2_recovery_disarm_healthy(void);

#define MCUCTRL_CHIPREV    (*(volatile const uint32_t *)0x4002000cu)
#define MCUCTRL_OTAPOINTER (*(volatile uint32_t *)0x40020264u)
#define G2_MRAM_RECOVERY_KEY 0xAFD1363Au   /* am_hal_mram_recovery.h */
#define CHIPREV_B1         0x22u           /* APOLLO5_B1; B2 = 0x23; B0 is < 0x22 */

/* Consecutive watchdog resets before recovery is armed. Deliberately high so
 * an isolated watchdog reset that then boots cleanly never escalates; only a
 * persistent early-boot crash loop (the brick signature) reaches it. */
#define G2_SELF_RECOVERY_THRESHOLD 5u
#define G2_SELF_RECOVERY_MAGIC     0x5245434Fu /* "RECO" */

/* Persistent across warm/watchdog reset: SSRAM .noinit, which the region table
 * (link/g2-apollo-main.ld keeps .noinit NOLOAD) never zeroes. Outside the DTCM
 * gap cleared by g2c_gnu_init.c Fix 43, so that zero row cannot touch it. */
struct g2_self_recovery_state {
    uint32_t magic;
    uint32_t wdt_streak;
    uint32_t armed;
};
__attribute__((section(".noinit.self_recovery"), aligned(4), used))
static volatile struct g2_self_recovery_state g2_self_recovery;

/* Arm application-initiated MRAM recovery (bReset=false). Returns 0 on success,
 * non-zero if the chip revision does not support it (APOLLO5_B0). */
uint32_t g2_mram_recovery_arm(void)
{
    if ((MCUCTRL_CHIPREV & 0xffu) < CHIPREV_B1)
        return 1u; /* APOLLO5_B0: unsupported, as in the upstream HAL */
    MCUCTRL_OTAPOINTER = G2_MRAM_RECOVERY_KEY;
    return 0u;
}

/* Crash-loop gate. Call once early in boot with the latched reset-cause flags
 * (g2_reset_status): wdt_reset = watchdog fired, clean_reset = power-on or
 * external reset (an intentional user restart). Arms recovery only after
 * G2_SELF_RECOVERY_THRESHOLD consecutive watchdog resets with no clean reset
 * between them. */
void g2_self_recovery_boot_check(bool wdt_reset, bool clean_reset)
{
    struct g2_self_recovery_state *s = &g2_self_recovery;

    if (s->magic != G2_SELF_RECOVERY_MAGIC) { /* cold boot / uninitialised RAM */
        s->magic = G2_SELF_RECOVERY_MAGIC;
        s->wdt_streak = 0u;
        s->armed = 0u;
        return;
    }
    if (clean_reset) {               /* user power-cycle / external reset */
        s->wdt_streak = 0u;
        s->armed = 0u;
        return;
    }
    if (wdt_reset && s->wdt_streak < 0xffffu)
        s->wdt_streak++;
    if (s->wdt_streak >= G2_SELF_RECOVERY_THRESHOLD && s->armed == 0u) {
        if (g2_mram_recovery_arm() == 0u)
            s->armed = 1u;
    }
}

/* Clear the crash-loop counter once the application is confirmed healthy
 * (e.g. BLE advertising / OTA receiver ready). A device that reaches this on
 * every good boot can never accumulate toward the arming threshold. */
void g2_self_recovery_mark_healthy(void)
{
    g2_self_recovery.wdt_streak = 0u;
    g2_self_recovery.armed = 0u;
}

/* ---------------------------------------------------------------------------
 * Recovery experiment (2026-11-01): unconditional early arm + healthy disarm.
 *
 * g2_recovery_arm_early() is called from low_level_init_5e4228() (IAR cstartup,
 * before RAM-init and before board_init / the ADC hw-id poll), so it runs even
 * on a boot that later hangs early. It arms MRAM wired-recovery unconditionally
 * (MCUCTRL->OTAPOINTER = key), after saving the genuine pre-arm OTAPOINTER in a
 * persistent .noinit cell. The key write is pure MMIO and needs no initialised
 * RAM, so recovery is armed even if everything else is still uninitialised.
 *
 * g2_recovery_disarm_healthy() is called from DEV_BoxRevcMsgProcess_53a0b6()
 * after the temple has answered a charging-case product-test frame -- i.e. the
 * scheduler, device-manager thread and pogo UART are all alive and the temple
 * is talking to the case. It restores the saved OTAPOINTER so the NEXT reset
 * boots the app normally instead of entering SBL wired-load.
 *
 * Net effect: a flash that still hangs early never reaches the disarm, so the
 * temple comes up in SBL wired-load on the next reset and is recoverable over
 * the case pogo link (the one untested recovery route); a flash that boots and
 * talks to the case disarms itself and reboots normally. Only a temple used
 * entirely out of the case would not disarm (add a BLE-advertising disarm for
 * that case). Not stock firmware. See g2/docs/reference/self-recovery-arming.md.
 * ------------------------------------------------------------------------- */

#define G2_RECOVERY_SAVE_MAGIC 0x4f544150u /* "OTAP" */

__attribute__((section(".noinit.recovery_save"), aligned(4), used))
static volatile struct {
    uint32_t magic;
    uint32_t orig_otap;   /* genuine pre-arm OTAPOINTER, kept across warm resets */
} g2_recovery_save;

void g2_recovery_arm_early(void)
{
    if ((MCUCTRL_CHIPREV & 0xffu) < CHIPREV_B1)
        return; /* APOLLO5_B0: application-initiated recovery unsupported */

    uint32_t cur = MCUCTRL_OTAPOINTER;
    if (g2_recovery_save.magic != G2_RECOVERY_SAVE_MAGIC) {
        /* First boot since a cold (POA) start: capture the real OTA pointer so
         * disarm can restore it. Never capture our own key as the "original". */
        g2_recovery_save.orig_otap = (cur == G2_MRAM_RECOVERY_KEY) ? 0u : cur;
        g2_recovery_save.magic = G2_RECOVERY_SAVE_MAGIC;
    }
    MCUCTRL_OTAPOINTER = G2_MRAM_RECOVERY_KEY; /* arm, bReset=false */
}

void g2_recovery_disarm_healthy(void)
{
    if (g2_recovery_save.magic != G2_RECOVERY_SAVE_MAGIC)
        return; /* never armed this power cycle */
    if (MCUCTRL_OTAPOINTER == G2_MRAM_RECOVERY_KEY)
        MCUCTRL_OTAPOINTER = g2_recovery_save.orig_otap; /* restore -> disarm */
}
