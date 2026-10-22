/* MX25U25643G MSPI1 controller bring-up, stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\flash\drv_mx25u25643g.c,
 * function string "am_devices_norflash_qspi_init" (ROM 0x75f930).
 * Native 0x46fb0c..0x46fe37 (812 bytes); literal pools 0x470014, 0x4700a4,
 * 0x4700a8 and 0x470668..0x470868. Sole caller DRV_Mx25u25643g_init
 * (0x46fe38, drivers/flash/mx25u25643g/drv_mx25u25643g.c) with devcfg NULL.
 *
 * Sequence (am_devices_mspi_* init shape): claim the single device slot,
 * am_hal_mspi_initialize / power_control(WAKE) / configure (TCB 0x100 words
 * at SSRAM 0x203799a0) / device_configure (caller config, else the quad
 * config at RAM 0x20000808) / enable; then the board pin and clock hooks,
 * pin 103 config read (result unused), XIP config (stock request 18, 16-byte
 * ROM record 0x785d00) and XIP enable (stock request 21; the stock HAL request
 * enum sits two entries above the pinned 5.1.0 one), MSPI interrupts 0x1a80,
 * NVIC IRQ 21 (MSPI1) priority 4, global interrupt enable, and publish the
 * slot. Stock quirk kept: with no caller config the slot's mode byte is taken
 * from the serial config at RAM 0x200007f0 (+8), not from 0x20000808.
 * Configure/device/enable failures deinitialize the handle; the power-on,
 * interrupt-clear and interrupt-enable failures return 1 without it. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define MX25U_MAX_DEVICES 1u
#define MSPI1_IRQ 21
#define MSPI1_IRQ_PRIORITY 4u
#define MSPI_INT_MASK 0x1a80u
#define MSPI_TCB_WORDS 0x100u
#define MSPI_REQ_XIP_CONFIG 18u /* stock numbering */
#define MSPI_REQ_XIP_EN 21u     /* stock numbering */
#define BSP_FLASH_GPIO 103u
#define BSP_MSPI_PINS_FLASH 16u

typedef struct {
    uint32_t module;   /* +0x0 */
    uint32_t mode;     /* +0x4 device-config byte +8 */
    void *handle;      /* +0x8 HAL handle */
    uint8_t occupied;  /* +0xc */
    uint8_t pad[3];
} g2_mx25u_device_t;
_Static_assert(sizeof(g2_mx25u_device_t) == 16, "slot record is 16 bytes");

/* am_hal_mspi_config_t. */
typedef struct {
    uint32_t tcb_size;  /* +0x0 words */
    uint32_t *tcb;      /* +0x4 */
    bool clk_on_d4;     /* +0x8 */
} g2_mspi_config_t;

/* Storage owned by this driver object. Addresses from the 0x470668..0x470860
 * literal pool; .data values from the decoded 0x20000000 init stream, ROM
 * bytes from the 2.2.6.10 main image. fal-norflash-entry-exit.c still reaches
 * the two device configurations by raw address. */

/* RAM 0x20073e34 (.bss, beyond the init stream): the single device slot. */
g2_mx25u_device_t g2_mx25u_devices_20073e34[MX25U_MAX_DEVICES];

/* SSRAM 0x203799a0 (.bss): MSPI1 command-queue TCB, 0x100 words; the uLED
 * work buffer ends 0x400 bytes earlier (display_driver_uled_work_buffer.c). */
uint32_t g2_mx25u_mspi_tcb_203799a0[MSPI_TCB_WORDS];

/* am_hal_mspi_dev_config_t (24 bytes).
 * RAM 0x200007f0 (.data): serial NOR configuration, byte +8 = 0. */
uint8_t g2_norflash_serial_devcfg_200007f0[24] = {
    0x08, 0x03, 0x00, 0x00, 0x03, 0x00, 0x02, 0x00,
    0x00, 0x00, 0x00, 0x14, 0x00, 0x01, 0x01, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};

/* RAM 0x20000808 (.data): quad NOR configuration (read opcode 0x6b, byte
 * +8 = 0x10), the default device_configure argument. */
uint8_t g2_norflash_quad_devcfg_20000808[24] = {
    0x08, 0x03, 0x00, 0x00, 0x6b, 0x00, 0x02, 0x00,
    0x10, 0x00, 0x00, 0x14, 0x00, 0x01, 0x01, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};

/* ROM 0x785d00: am_hal_mspi_xip_config_t for stock request 18. */
const uint8_t g2_mx25u_xip_config_785d00[16] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x80, 0x01, 0x09, 0x00, 0x00,
};

extern volatile uint32_t g2_norflash_controller_handle_20074544;       /* RAM 0x20074544 */

extern uint32_t am_hal_mspi_initialize(uint32_t module, void **handle);          /* 0x4c0812 */
extern uint32_t am_hal_mspi_power_control(void *handle, uint32_t state, bool retain); /* 0x4c26e0 */
extern uint32_t am_hal_mspi_configure(void *handle, const g2_mspi_config_t *cfg); /* 0x4c08a8 */
extern uint32_t am_hal_mspi_device_configure(void *handle, const void *devcfg);  /* 0x4c099c */
extern uint32_t am_hal_mspi_enable(void *handle);                                /* 0x4c0e1e */
extern uint32_t am_hal_mspi_deinitialize(void *handle);                          /* 0x4c0f24 */
extern uint32_t g2_norflash_config_transfer_4c0f78(uint32_t controller, uint32_t request,
                                                   const void *payload);         /* am_hal_mspi_control */
extern uint32_t am_hal_mspi_interrupt_clear(void *handle, uint32_t mask);        /* 0x4c23de */
extern uint32_t am_hal_mspi_interrupt_enable(void *handle, uint32_t mask);       /* 0x4c2328 */
extern uint32_t am_hal_gpio_pinconfig_get(uint32_t pin, uint32_t *cfg);          /* 0x480eee */
extern uint32_t am_hal_interrupt_master_enable(void);                            /* 0x473934 */
extern void g2_norflash_mode_select_46f6ba(uint32_t mode);
extern void g2_norflash_clock_select_4c32b4(uint32_t controller, uint32_t mode); /* am_bsp_mspi_pins_enable */
extern void nvic_enable_irq_46f4a4(int16_t irq);
extern void nvic_set_priority_46f4c2(int16_t irq, uint32_t priority);
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

uint32_t mx25u25643g_mspi_init_46fb0c(uint32_t module, const void *devcfg, void **context);

static const char module_tag[] = "drv.norflash"; /* ROM 0x785cd0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c"; /* ROM 0x70258c */
static const char init_fn[] = "am_devices_norflash_qspi_init"; /* ROM 0x75f930 */
static const char power_fail[] = "Error - Failed to power on MSPI.\n"; /* ROM 0x753e4c */
static const char power_fail_short[] = "[drv.norflash]Error - Failed to power on MSPI.\n"; /* ROM 0x733884 */
static const char config_fail[] = "Error - Failed to configure MSPI.\n"; /* ROM 0x753e70 */
static const char config_fail_short[] = "[drv.norflash]Error - Failed to configure MSPI.\n"; /* ROM 0x72917c */
static const char device_fail[] = "Error - Failed to configure MSPI device.\n"; /* ROM 0x73e6e4 */
static const char device_fail_short[] = "[drv.norflash]Error - Failed to configure MSPI device.\n"; /* ROM 0x71e648 */
static const char enable_fail[] = "Error - Failed to enable MSPI.\n"; /* ROM 0x75f950 */
static const char enable_fail_short[] = "[drv.norflash]Error - Failed to enable MSPI.\n"; /* ROM 0x7338b4 */
static const char irq_fail[] = "Error - Failed to enable interrupt .\n"; /* ROM 0x749ac4 */
static const char irq_fail_short[] = "[drv.norflash]Error - Failed to enable interrupt .\n"; /* ROM 0x7291b0 */
static const char init_ok[] = "MX25U25643G mSPI interface initialized."; /* ROM 0x749aec */
static const char init_ok_short[] = "[drv.norflash]MX25U25643G mSPI interface initialized."; /* ROM 0x71e680 */

static void log_line(uint8_t level, uint32_t line, const char *text, uint32_t short_flags,
                     const char *short_text)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, init_fn, line, text);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(short_flags, short_text, short_text);
}

/* Stock 0x46fb0c. Returns 0, 0xffffffff when the slot is taken, 1 for the
 * power/interrupt failures, else the failing HAL status. */
uint32_t mx25u25643g_mspi_init_46fb0c(uint32_t module, const void *devcfg, void **context)
{
    g2_mspi_config_t cfg = {0u, NULL, false};
    uint32_t pin_cfg;
    uint8_t xip[16];
    uint32_t status;
    uint32_t slot;

    for (slot = 0u; slot < MX25U_MAX_DEVICES; slot++) {
        if (g2_mx25u_devices_20073e34[slot].occupied == 0u)
            break;
    }
    if (slot == MX25U_MAX_DEVICES)
        return 0xffffffffu;

    void **handle = (void **)(uintptr_t)&g2_norflash_controller_handle_20074544;
    status = am_hal_mspi_initialize(module, handle);
    if (status != 0u)
        return status;

    if (am_hal_mspi_power_control(*handle, 0u, false) != 0u) {
        log_line(1u, 0x22au, power_fail, 0x04000000u, power_fail_short);
        return 1u;
    }

    cfg.tcb_size = MSPI_TCB_WORDS;
    cfg.tcb = g2_mx25u_mspi_tcb_203799a0;
    cfg.clk_on_d4 = false;
    status = am_hal_mspi_configure(*handle, &cfg);
    if (status != 0u) {
        log_line(1u, 0x233u, config_fail, 0x04000000u, config_fail_short);
        (void)am_hal_mspi_deinitialize(*handle);
        return status;
    }

    if (devcfg != NULL)
        status = am_hal_mspi_device_configure(*handle, devcfg);
    else
        status = am_hal_mspi_device_configure(*handle, g2_norflash_quad_devcfg_20000808);
    if (status != 0u) {
        log_line(1u, 0x23fu, device_fail, 0x04000000u, device_fail_short);
        (void)am_hal_mspi_deinitialize(*handle);
        return status;
    }

    status = am_hal_mspi_enable(*handle);
    if (status != 0u) {
        log_line(1u, 0x246u, enable_fail, 0x04000000u, enable_fail_short);
        (void)am_hal_mspi_deinitialize(*handle);
        return status;
    }

    g2_norflash_mode_select_46f6ba(0u);
    g2_norflash_clock_select_4c32b4(module, BSP_MSPI_PINS_FLASH);
    (void)am_hal_gpio_pinconfig_get(BSP_FLASH_GPIO, &pin_cfg);

    (void)audio_uart_display_area_copy_439c04(xip, g2_mx25u_xip_config_785d00, sizeof(xip));
    status = g2_norflash_config_transfer_4c0f78((uint32_t)(uintptr_t)*handle, MSPI_REQ_XIP_CONFIG, xip);
    if (status != 0u)
        return status;
    status = g2_norflash_config_transfer_4c0f78((uint32_t)(uintptr_t)*handle, MSPI_REQ_XIP_EN, NULL);
    if (status != 0u)
        return status;

    if (am_hal_mspi_interrupt_clear(*handle, MSPI_INT_MASK) != 0u)
        return 1u;
    if (am_hal_mspi_interrupt_enable(*handle, MSPI_INT_MASK) != 0u) {
        log_line(1u, 0x269u, irq_fail, 0x04000000u, irq_fail_short);
        return 1u;
    }

    nvic_set_priority_46f4c2(MSPI1_IRQ, MSPI1_IRQ_PRIORITY);
    nvic_enable_irq_46f4a4(MSPI1_IRQ);
    (void)am_hal_interrupt_master_enable();

    g2_mx25u_device_t *d = &g2_mx25u_devices_20073e34[slot];
    d->module = module;
    if (devcfg != NULL)
        d->mode = ((const uint8_t *)devcfg)[8];
    else
        d->mode = g2_norflash_serial_devcfg_200007f0[8];
    d->handle = *handle;
    d->occupied = 1u;
    *context = d;

    log_line(3u, 0x27au, init_ok, 0x0c000000u, init_ok_short);
    return 0u;
}
