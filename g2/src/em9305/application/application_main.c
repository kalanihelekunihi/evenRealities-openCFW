/* EM9305 product application entry (first-party application code linked into
 * the NVM image, not an EM SDK archive object).
 * Native 0x30eb8c..0x30ec9a (application entry, including the warm-resume
 * tail at 0x30ec92) and the IRQ 6 wake callback 0x306894..0x3068c6.
 * Stock source path unknown (no log strings in this image).
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* EM9305 peripheral registers touched by the wake-pin mirror. */
#define G2_EM_REG(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define G2_EM_WAKE_PIN_IN      0xf0343cu /* bit 6 = wake input level */
#define G2_EM_WAKE_PIN_CTRL    0xf03440u /* bit 6 mirrored from input */
#define G2_EM_WAKE_CFG_428     0xf01428u
#define G2_EM_WAKE_CFG_42C     0xf0142cu
#define G2_EM_WAKE_CFG_438     0xf01438u
#define G2_EM_WAKE_CFG_448     0xf01448u

/* HCI command table record used by ROM 0x10207c: {handler, guard, opcode}.
 * Guard words seen: 0, 0xa9a9a9a9, 0x53535353. */
struct g2_em_hci_cmd_entry {
    uint32_t handler;  /* +0 */
    uint32_t guard;    /* +4 */
    uint16_t opcode;   /* +8 (0xfcxx EM vendor commands, 0x0c03 HCI_Reset) */
    uint16_t pad;      /* +10 */
};
_Static_assert(sizeof(struct g2_em_hci_cmd_entry) == 12, "command record size");

extern const struct g2_em_hci_cmd_entry g2_em_hci_cmd_table_334254[]; /* ROM 0x334254 */
extern const struct g2_em_hci_cmd_entry g2_em_hci_cmd_table_334954[]; /* ROM 0x334954 */
extern const struct g2_em_hci_cmd_entry g2_em_hci_cmd_table_3340bc[]; /* ROM 0x3340bc */
extern const uint16_t g2_em_hci_cmd_count_334952; /* ROM 0x334952 = 11 */
extern const uint16_t g2_em_hci_cmd_count_334ae0; /* ROM 0x334ae0 = 33 */
extern const uint16_t g2_em_hci_cmd_count_334950; /* ROM 0x334950 = 12 */

/* Optional product start callback, called (0xff, 1, &flag, 0). RAM 0x8010a4 */
extern void (*g2_em_app_start_callback)(uint32_t, uint32_t, uint8_t *, uint32_t);

extern void BSP_Init(void);                                      /* 0x302e80 */
extern void irq_set_user_callback_3069b8(void (*callback)(uint32_t));
extern uint32_t opencfw_em9305_controller_rom_register_irq(uint32_t, uint32_t, uint32_t, uint32_t); /* ROM 0x1035dc */
extern void opencfw_em9305_sleep_controller_enable(uint32_t, uint32_t, uint32_t); /* PML_RegisterWakeUpAction 0x30f6ec */
extern uint32_t opencfw_em9305_controller_rom_boot_status(uint32_t); /* ROM 0x103678 */
extern uint32_t opencfw_em9305_controller_rom_boot_ready(uint32_t);  /* ROM 0x10361c */
extern void em9305_rom_hci_cmd_init_101f14(void);
extern void em9305_rom_hci_cmd_table_register_10207c(const struct g2_em_hci_cmd_entry *table, uint32_t count);
extern void em9305_rom_hci_vs_handler_register_1026bc(uintptr_t handler);
extern void em9305_rom_resume_prepare_1020d4(void);
extern void wsf_os_init_only_veneer_30460c(void);   /* tail to WsfOsInitOnly 0x314068 */
extern void wsf_os_register_start_304610(void);     /* WsfOsRegisterTaskInitCback(0x302a20); WsfOsStartOnly() */
extern void myapp_ctor_30ea08(void);
extern void myapp_start_30eabc(void);
extern uint32_t lhciCmdVsExtInterfaceEM(void);      /* 0x32e5a8, passed by address only */
extern _Noreturn void opencfw_em9305_framework_run(void);    /* QF_run 0x311230 */
extern _Noreturn void opencfw_em9305_framework_resume(void); /* QF_resume 0x311218 */

_Noreturn void qf_resume_caller(void);

/* Mirror the wake input level (bit 6) into the wake configuration. The stock
 * code loads R0 = 3 in a branch delay slot on both paths, so the "set" path
 * writes 3 | bit 11 = 0x803. */
static void application_wake_pin_mirror(void)
{
    uint32_t level = G2_EM_REG(G2_EM_WAKE_PIN_IN);
    if ((level & (1u << 6)) == 0u) {
        G2_EM_REG(G2_EM_WAKE_CFG_42C) = 0u;
        G2_EM_REG(G2_EM_WAKE_PIN_CTRL) &= ~(1u << 6);
    } else {
        G2_EM_REG(G2_EM_WAKE_CFG_42C) = 3u | (1u << 11);
        G2_EM_REG(G2_EM_WAKE_CFG_448) = 0u;
        G2_EM_REG(G2_EM_WAKE_PIN_CTRL) |= 1u << 6;
    }
}

/* Stock 0x00306894 (em_vendor_system; IRQ 6 wake callback that the
 * application entry registers). Same register sequence as the entry. */
void application_gpio_wake_irq_306894(uint32_t irq)
{
    if (irq != 6u) return;
    application_wake_pin_mirror();
}

/* Stock 0x0030EB8C (application_hook: NVM application entry, hook-table target) */
_Noreturn void application_main_30eb8c(void)
{
    uint8_t start_flag;

    BSP_Init();
    __asm__ volatile("seti 0" ::: "memory");
    irq_set_user_callback_3069b8(application_gpio_wake_irq_306894);
    (void)opencfw_em9305_controller_rom_register_irq(6u, 1u, 1u, 1u);
    opencfw_em9305_sleep_controller_enable(0u, 0x40u, 1u);

    G2_EM_REG(G2_EM_WAKE_CFG_42C) = 0u;
    G2_EM_REG(G2_EM_WAKE_CFG_428) = 0x1e100u;
    G2_EM_REG(G2_EM_WAKE_CFG_438) = 1u;
    application_wake_pin_mirror();

    /* Warm boot (status bits 8..9 set and ROM "ready" == 0): resume QF. */
    if ((opencfw_em9305_controller_rom_boot_status(3u) & 0x300u) != 0u &&
        opencfw_em9305_controller_rom_boot_ready(3u) == 0u)
        qf_resume_caller();

    em9305_rom_hci_cmd_init_101f14();
    em9305_rom_hci_cmd_table_register_10207c(g2_em_hci_cmd_table_334254, g2_em_hci_cmd_count_334952);
    em9305_rom_hci_cmd_table_register_10207c(g2_em_hci_cmd_table_334954, g2_em_hci_cmd_count_334ae0);
    em9305_rom_hci_cmd_table_register_10207c(g2_em_hci_cmd_table_3340bc, g2_em_hci_cmd_count_334950);
    wsf_os_init_only_veneer_30460c();
    wsf_os_register_start_304610();
    myapp_ctor_30ea08();
    myapp_start_30eabc();
    em9305_rom_hci_vs_handler_register_1026bc((uintptr_t)&lhciCmdVsExtInterfaceEM);

    start_flag = 1u;
    if (g2_em_app_start_callback != NULL)
        g2_em_app_start_callback(0xffu, 1u, &start_flag, 0u);

    opencfw_em9305_framework_run(); /* stock follows with a KFLAG 1 halt loop */
}

/* Stock 0x0030EC92 (qf_resume_caller: warm-boot tail of the application entry) */
_Noreturn void qf_resume_caller(void)
{
    em9305_rom_resume_prepare_1020d4();
    opencfw_em9305_framework_resume();
}
