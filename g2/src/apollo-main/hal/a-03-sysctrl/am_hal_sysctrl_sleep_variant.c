/* AmbiqSuite Apollo510 HAL am_hal_sysctrl_sleep (mcu/am_hal_sysctrl.c, BSD-3-Clause),
 * stock variant. Native 0x44ab42..0x44b067, literal pool 0x44b4fc..0x44b56b
 * (shared with am_hal_sysctrl_clkmuxrst_low_power_init 0x44b158).
 *
 * Differs from the pinned public 5.1.0 replay (third-party/upstream/ambiqhal-apollo510
 * 5efc022) as follows:
 *  - normal sleep programs ELP/CLP = 1/1 (ON_CLK_OFF) for both SLEEPMODE settings
 *    and keeps an active ELP of RET(2) or OFF(3); 5.1.0 uses ELP_RET;
 *  - no NO_TEMPSENSE_IN_DEEPSLEEP / AM_HAL_PRE_SLEEP_PROCESSING hook; two NOPs
 *    follow the first SYNC_READ flush instead;
 *  - the boost-timer re-sleep path tests VECTPENDING against the literal 98
 *    and its second flush/WFI omits the NOPs;
 *  - AM_HAL_STALL_CPU_HPWAKE is 0; the buck override restore sets
 *    VRCTRL bits 16, 0 and 5 (SIMOBUCKOVER, CORELDOOVER, MEMLDOOVER).
 * The register and spot-manager global addresses are the stock ones below. */
#include <stdint.h>
#include <stdbool.h>

#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define FLAG(a) (*(volatile uint8_t *)(uintptr_t)(a))

/* Peripheral registers. */
#define MCUCTRL_CHIPREV      0x4002000cu /* [7:0] 0x22 = B1, 0x23 = B2 */
#define MCUCTRL_VRCTRL       0x40020060u
#define MCUCTRL_SIMOBUCK2    0x40020344u /* VDDCACTLOWTONTRIM [29:25] */
#define MCUCTRL_SIMOBUCK14   0x40020374u /* VDDFCOMPTRIMMINUS [4:0] */
#define MCUCTRL_PWRSW0       0x4002037cu /* PWRSWVDDCPUOVERRIDE bit 3, PWRSWVDDCAOROVERRIDE bit 6 */
#define MCUCTRL_PLLCTL0      0x400204d8u /* SYSPLLPDB bit 29 */
#define PWRCTRL_MCUPERFREQ   0x40021000u /* MCUPERFREQ [1:0], MCUPERFSTATUS [4:3] */
#define PWRCTRL_DEVPWRSTATUS 0x40021008u /* PWRSTOTP bit 27 */
#define PWRCTRL_AUDSSPWRSTATUS 0x40021010u
#define PWRCTRL_CPUPWRCTRL   0x40021050u /* SLEEPMODE bit 2 */
#define PWRCTRL_VRSTATUS     0x40021108u /* SIMOBUCKST [5:4] */
#define SYNC_READ            0x47ff0000u
#define SCB_ICSR             0xe000ed04u /* VECTPENDING [20:12] */
#define SCB_SCR              0xe000ed10u
#define PWRMODCTL_CPDLPSTATE 0xe001e300u

/* Spot-manager / PCM globals (RAM). */
#define G_PCM_TRIM_VERSION         0x200001e8u /* uint32_t */
#define G_SPOTMGR_INFO1            0x2005665cu /* g_sSpotMgrINFO1regs */
#define G_IS_PCM2P1                0x20074f64u
#define G_IS_PCM2P2_OR_NEWER       0x20074f68u
#define G_VDDCAOR_VDDCPU_OVERRIDE  0x20074f6au
#define G_HP_TO_DEEPSLEEP          0x20074f6bu
#define G_VDDF_LP_MINUS_FOR_LP     0x20074f6cu
#define G_SWITCHING_TO_HP          0x20074f6du
#define G_FRC_BUCK_ACT             0x20074f7bu
#define G_APP_FRC_BUCK_ACT         0x20074f7cu

#define INFO1_GLOBAL_VALID   0x1f01600du
#define INFO1_GPUVDDCTON_OFF 0x54u /* GPULPCPUHPVDDCTON [9:5] */
#define INFO1_MEMLDOCFG_OFF  0x68u /* VDDFCOMPTRIMMINUS [24:20] */

#define SLEEP_DEEP 1u
#define MCU_MODE_HIGH_PERFORMANCE 2u
#define STIM_CPU_STATE 0u
#define CPUSTATE_ACTIVE_LP 0u
#define CPUSTATE_ACTIVE_HP 1u
#define CPUSTATE_SLEEP_DEEP 2u
#define ELP_ON_CLK_OFF 1u
#define ELP_RET 2u
#define ELP_OFF 3u
#define CLP_ON_CLK_OFF 1u
#define INTERNAL_TIMER_A_VECTOR 98u /* TIMER0_IRQn + AM_HAL_INTERNAL_TIMER_NUM_A + 16 */

/* am_hal_pwrctrl_pwrmodctl_cpdlp_t, passed by value as one word. */
typedef union {
    struct {
        uint8_t rlp; /* +0 */
        uint8_t elp; /* +1 */
        uint8_t clp; /* +2 */
        uint8_t pad; /* +3 */
    } f;
    uint32_t word;
} g2_cpdlp_t;
_Static_assert(sizeof(g2_cpdlp_t) == 4u, "cpdlp config word");

extern const uint32_t g2_sysctrl_ds_cpdlp_template; /* ROM 0x78ee5c = {0, ELP_RET, CLP_RET, 0} */

extern uint32_t g2_main_critical_save_473940(void);                 /* am_hal_interrupt_master_disable */
extern void am_hal_pwrctrl_pwrmodctl_cpdlp_get_480008(g2_cpdlp_t *config);
extern uint32_t stock_cpdlp_config(uint32_t config);                /* 0x47ffc4 am_hal_pwrctrl_pwrmodctl_cpdlp_config */
extern uint32_t audio_ble_flash_control(uint32_t device, uint32_t enabled,
                                        const uint32_t *command);   /* 0x480312 am_hal_spotmgr_power_state_update */
extern void buck_ldo_update_override_47fe6c(bool enable);           /* 0x47fe6c */
extern void am_hal_spotmgr_simobuck_lp_autosw_enable_480408(void);
extern void am_hal_spotmgr_simobuck_lp_autosw_disable_48041e(void);
extern void am_hal_spotmgr_boost_timer_interrupt_service_48039a(void);
extern void stock_delay_us(uint32_t us);                            /* 0x4807a0 am_hal_delay_us */

static void report_cpu_state(const uint8_t *state)
{
    (void)audio_ble_flash_control(STIM_CPU_STATE, 0u, (const uint32_t *)(const void *)state);
}

static uint32_t vectpending(void)
{
    return (REG(SCB_ICSR) >> 12) & 0x1ffu;
}

static void set_vddf_trim(uint32_t value)
{
    REG(MCUCTRL_SIMOBUCK14) = (REG(MCUCTRL_SIMOBUCK14) & ~0x1fu) | (value & 0x1fu);
}

static void clear_vddf_trim(void)
{
    REG(MCUCTRL_SIMOBUCK14) = (REG(MCUCTRL_SIMOBUCK14) >> 5) << 5;
}

static uint32_t info1_word(uint32_t offset)
{
    return REG(G_SPOTMGR_INFO1 + offset);
}

static void set_vddcact_trim(uint32_t value)
{
    REG(MCUCTRL_SIMOBUCK2) = (REG(MCUCTRL_SIMOBUCK2) & ~(0x1fu << 25)) | ((value & 0x1fu) << 25);
}

static void wait_hp_mode(void)
{
    while (((REG(PWRCTRL_MCUPERFREQ) >> 3) & 3u) != MCU_MODE_HIGH_PERFORMANCE)
        stock_delay_us(1u);
}

static bool buck_may_enter_lp(void)
{
    uint32_t rev = REG(MCUCTRL_CHIPREV) & 0xffu;
    uint32_t trim = REG(G_PCM_TRIM_VERSION);
    if (rev == 0x22u && trim >= 2u)  /* APOLLO5_B1_GE_PCM2P1 */
        return true;
    if (rev == 0x23u && trim != 0u)  /* APOLLO5_B2_GE_PCM2P1 */
        return true;
    return (REG(PWRCTRL_AUDSSPWRSTATUS) & 0x4c4u) == 0u &&
           (REG(PWRCTRL_DEVPWRSTATUS) & 0x3fffffffu) == 0u &&
           ((REG(MCUCTRL_PLLCTL0) >> 29) & 1u) == 0u;
}

static void pwrsw_override_clear(void)
{
    REG(MCUCTRL_PWRSW0) &= ~8u;
    REG(MCUCTRL_PWRSW0) &= ~0x40u;
}

static void pwrsw_override_set(void)
{
    REG(MCUCTRL_PWRSW0) |= 8u;
    REG(MCUCTRL_PWRSW0) |= 0x40u;
}

/* bSleepDeep: 1 = deep sleep, otherwise normal sleep. */
void am_hal_sysctrl_sleep_44ab42(bool bSleepDeep)
{
    bool buck_into_lp = false;
    bool periph_off = false;
    bool reported_deepsleep = false;
    bool vddcact_changed = false;
    bool pwrsw_override_at_wake = false;
    bool other_isr_pending = false;
    uint32_t saved_vddcact = 0u;
    uint32_t timer_vector = INTERNAL_TIMER_A_VECTOR;
    uint8_t cpu_state[2];
    g2_cpdlp_t active;
    g2_cpdlp_t sleep;

    uint32_t primask = g2_main_critical_save_473940();
    am_hal_pwrctrl_pwrmodctl_cpdlp_get_480008(&active);
    uint32_t cpdlp_restore = ((uint32_t)active.f.rlp << 8) | ((uint32_t)active.f.elp << 4) | active.f.clp;
    bool simobuck_active = ((REG(PWRCTRL_VRSTATUS) >> 4) & 3u) == 3u;

    if (bSleepDeep == SLEEP_DEEP && ((REG(PWRCTRL_DEVPWRSTATUS) >> 27) & 1u) == 0u) {
        sleep.word = g2_sysctrl_ds_cpdlp_template;
        sleep.f.rlp = active.f.rlp;
        if (active.f.elp == ELP_OFF)
            sleep.f.elp = ELP_OFF;
        (void)stock_cpdlp_config(sleep.word);

        cpu_state[0] = CPUSTATE_SLEEP_DEEP;
        report_cpu_state(&cpu_state[0]);
        cpu_state[0] = (REG(PWRCTRL_MCUPERFREQ) & 3u) == MCU_MODE_HIGH_PERFORMANCE ? CPUSTATE_ACTIVE_HP
                                                                                    : CPUSTATE_ACTIVE_LP;
        reported_deepsleep = true;

        if (simobuck_active && buck_may_enter_lp()) {
            periph_off = true;
            if (FLAG(G_APP_FRC_BUCK_ACT) == 0u && FLAG(G_FRC_BUCK_ACT) == 0u) {
                buck_into_lp = true;
                buck_ldo_update_override_47fe6c(false);
                am_hal_spotmgr_simobuck_lp_autosw_enable_480408();
            }
        }
        REG(SCB_SCR) |= 4u;
        if ((REG(PWRCTRL_MCUPERFREQ) & 3u) == MCU_MODE_HIGH_PERFORMANCE)
            wait_hp_mode();
        if (FLAG(G_HP_TO_DEEPSLEEP) != 0u) {
            set_vddf_trim(info1_word(INFO1_MEMLDOCFG_OFF) >> 20);
            if (FLAG(G_VDDCAOR_VDDCPU_OVERRIDE) != 0u)
                pwrsw_override_clear();
            pwrsw_override_at_wake =
                (FLAG(G_IS_PCM2P2_OR_NEWER) != 0u && FLAG(G_VDDCAOR_VDDCPU_OVERRIDE) != 0u) ||
                (FLAG(G_IS_PCM2P1) != 0u && FLAG(G_VDDCAOR_VDDCPU_OVERRIDE) != 0u &&
                 FLAG(G_SWITCHING_TO_HP) == 0u);
        }
        if (FLAG(G_VDDF_LP_MINUS_FOR_LP) != 0u)
            set_vddf_trim(11u);
        if (info1_word(0u) == INFO1_GLOBAL_VALID && FLAG(G_IS_PCM2P1) != 0u) {
            uint32_t ton = (info1_word(INFO1_GPUVDDCTON_OFF) >> 5) & 0x1fu;
            uint32_t current = (REG(MCUCTRL_SIMOBUCK2) >> 25) & 0x1fu;
            if (ton < current) {
                saved_vddcact = current;
                set_vddcact_trim(info1_word(INFO1_GPUVDDCTON_OFF) >> 5);
                vddcact_changed = true;
            }
        }
    } else {
        /* Both SLEEPMODE settings (CPUPWRCTRL bit 2) select the same config;
         * byte 3 of the word is left unset as in stock. */
        if (((REG(PWRCTRL_CPUPWRCTRL) >> 2) & 1u) == 0u) {
            sleep.f.rlp = active.f.rlp;
            sleep.f.elp = ELP_ON_CLK_OFF;
            sleep.f.clp = CLP_ON_CLK_OFF;
        } else {
            sleep.f.rlp = active.f.rlp;
            sleep.f.elp = ELP_ON_CLK_OFF;
            sleep.f.clp = CLP_ON_CLK_OFF;
        }
        if (active.f.elp == ELP_OFF || active.f.elp == ELP_RET)
            sleep.f.elp = active.f.elp;
        (void)stock_cpdlp_config(sleep.word);
        REG(SCB_SCR) &= ~4u;
    }

    (void)REG(SYNC_READ);
    __asm__ volatile("nop\n\tnop" ::: "memory");
    __asm__ volatile("wfi" ::: "memory");
    __asm__ volatile("isb sy" ::: "memory");

    if (vddcact_changed)
        set_vddcact_trim(saved_vddcact);
    if (FLAG(G_HP_TO_DEEPSLEEP) != 0u) {
        if (pwrsw_override_at_wake)
            pwrsw_override_set();
        clear_vddf_trim();
    }
    if (FLAG(G_VDDF_LP_MINUS_FOR_LP) != 0u)
        clear_vddf_trim();

    /* Woken only by the spot-manager boost timer: service it and sleep again. */
    if ((FLAG(G_IS_PCM2P1) != 0u || FLAG(G_IS_PCM2P2_OR_NEWER) != 0u) && vectpending() == timer_vector) {
        am_hal_spotmgr_boost_timer_interrupt_service_48039a();
        if (vectpending() == 0u) {
            if (bSleepDeep == SLEEP_DEEP && (REG(PWRCTRL_MCUPERFREQ) & 3u) == MCU_MODE_HIGH_PERFORMANCE) {
                while (((REG(PWRCTRL_MCUPERFREQ) >> 3) & 3u) != MCU_MODE_HIGH_PERFORMANCE) {
                    if (vectpending() != 0u) {
                        other_isr_pending = true;
                        break;
                    }
                    stock_delay_us(1u);
                }
            }
            if (!other_isr_pending) {
                if (reported_deepsleep) {
                    report_cpu_state(&cpu_state[0]);
                    cpu_state[1] = CPUSTATE_SLEEP_DEEP;
                    report_cpu_state(&cpu_state[1]);
                }
                if (periph_off && FLAG(G_APP_FRC_BUCK_ACT) == 0u && FLAG(G_FRC_BUCK_ACT) == 0u) {
                    buck_into_lp = true;
                    buck_ldo_update_override_47fe6c(false);
                    am_hal_spotmgr_simobuck_lp_autosw_enable_480408();
                }
                if (FLAG(G_HP_TO_DEEPSLEEP) != 0u) {
                    set_vddf_trim(info1_word(INFO1_MEMLDOCFG_OFF) >> 20);
                    if (FLAG(G_VDDCAOR_VDDCPU_OVERRIDE) != 0u)
                        pwrsw_override_clear();
                }
                if (FLAG(G_VDDF_LP_MINUS_FOR_LP) != 0u)
                    set_vddf_trim(11u);
                if (vddcact_changed)
                    set_vddcact_trim(info1_word(INFO1_GPUVDDCTON_OFF) >> 5);
                (void)REG(SYNC_READ);
                __asm__ volatile("wfi" ::: "memory");
                __asm__ volatile("isb sy" ::: "memory");
                if (vddcact_changed)
                    set_vddcact_trim(saved_vddcact);
                if (FLAG(G_HP_TO_DEEPSLEEP) != 0u) {
                    if (pwrsw_override_at_wake)
                        pwrsw_override_set();
                    clear_vddf_trim();
                }
                if (FLAG(G_VDDF_LP_MINUS_FOR_LP) != 0u)
                    clear_vddf_trim();
            }
        }
    }

    if (FLAG(G_HP_TO_DEEPSLEEP) != 0u) {
        FLAG(G_HP_TO_DEEPSLEEP) = 0u;
        FLAG(G_VDDCAOR_VDDCPU_OVERRIDE) = 0u;
    }
    if (FLAG(G_VDDF_LP_MINUS_FOR_LP) != 0u)
        FLAG(G_VDDF_LP_MINUS_FOR_LP) = 0u;
    if (reported_deepsleep)
        report_cpu_state(&cpu_state[0]);
    if (buck_into_lp) {
        REG(MCUCTRL_VRCTRL) |= 0x10000u; /* SIMOBUCKOVER */
        REG(MCUCTRL_VRCTRL) |= 1u;       /* CORELDOOVER */
        REG(MCUCTRL_VRCTRL) |= 0x20u;    /* MEMLDOOVER */
    }
    am_hal_spotmgr_simobuck_lp_autosw_disable_48041e();
    REG(PWRMODCTL_CPDLPSTATE) = cpdlp_restore;
    __asm__ volatile("msr primask, %0" : : "r"(primask) : "memory");
}
