/* Product GPIO HAL. No source path string survives; the unit sits between
 * the box UART manager and drv_bq25180.c and mirrors driver\hal\src\hal_i2c.c,
 * so presumably D:\01_workspace\s200_ap510b_iar_git\driver\hal\src\hal_gpio.c.
 * Native 0x53a414..0x53a651; literal pool 0x53a654..0x53a66f.
 *
 * Contents: file-local CMSIS __NVIC_EnableIRQ / __NVIC_SetPriority copies,
 * the board pin-table initialiser, the input read helper and the three
 * GPIO0 bank ISRs (vector slots 0x438120/24/28 = IRQ 56..58).
 * The GPIO write wrapper 0x53a5be lives in
 * drivers/codec-host/codec-gpio-selector/gpio.c (g2_codec_pin_write). */
#include <stdint.h>
#include <stdbool.h>
#include "g2_hal_gpio.h"

#define NVIC_ISER_BASE 0xe000e100u
#define NVIC_IPR_BASE 0xe000e400u
#define SCB_SHPR_BASE 0xe000ed18u
#define GPIO_IRQ_PRIORITY 4u
#define GPIO_INT_CHANNEL_0 0u
#define GPIO_INT_CTRL_INDV_ENABLE 1u
#define GPIO_READ_INPUT 0u
#define GPIO_MASK_WORDS 7u /* am_hal_gpio_mask_t, 0x1c bytes */

/* am_hal_gpio_pincfg_t words (ROM consts of am_hal_gpio.c). */
extern const uint32_t g2_gpio_pincfg_output;   /* ROM 0x78f0f8 = 0x183 */
extern const uint32_t g2_gpio_pincfg_input;    /* ROM 0x78f0fc = 0x093 */
extern const uint32_t g2_gpio_pincfg_disabled; /* ROM 0x78f100 = 0x003 */
/* GPIO0 bank IRQ numbers {56, 57, 58, 59}, indexed by pin >> 5. */
extern const int16_t g2_gpio_bank_irq_78d6cc[]; /* ROM 0x78d6cc */

extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);
extern int32_t g2_gpio_hal_write(uint32_t pin, uint32_t mode); /* 0x480fd6 am_hal_gpio_state_write */
extern uint32_t audio_uart_pin_read(uint32_t pin, uint32_t mode, uint32_t *value); /* 0x480f8a am_hal_gpio_state_read */
extern uint32_t audio_ble_hci_radio_pin_mask_4810b0(uint32_t bank, uint32_t operation,
                                                    uint32_t *pins); /* am_hal_gpio_interrupt_control */
extern uint32_t am_hal_gpio_interrupt_status_get_4812f6(uint32_t channel, bool enabled_only,
                                                        uint32_t *mask);
extern uint32_t am_hal_gpio_interrupt_clear_481468(uint32_t channel, uint32_t *mask);
extern uint32_t am_hal_gpio_interrupt_irq_status_get_481574(uint32_t irq, bool enabled_only,
                                                            uint32_t *status);
extern uint32_t am_hal_gpio_interrupt_irq_clear_4815f2(uint32_t irq, uint32_t mask);
extern uint32_t audio_ble_hci_radio_register_48162c(uint8_t target, uint32_t event,
                                                    const void *handler,
                                                    uint32_t context); /* am_hal_gpio_interrupt_register */
extern uint32_t am_hal_gpio_interrupt_service_4816c6(uint32_t irq, uint32_t mask);
extern void audio_uart_lv_memzero_48949c(void *destination, uint32_t size);

void nvic_enable_irq_53a414(int16_t irq);
void nvic_set_priority_53a430(int16_t irq, uint32_t priority);
void am_gpio0_001f_isr_53a5e0(void);
void am_gpio0_203f_isr_53a606(void);
void am_gpio0_405f_isr_53a62c(void);

/* 0x53a414 */
void nvic_enable_irq_53a414(int16_t irq)
{
    if (irq >= 0) {
        ((volatile uint32_t *)NVIC_ISER_BASE)[(uint32_t)(int32_t)irq >> 5] =
            1u << ((uint32_t)irq & 0x1fu);
    }
}

/* 0x53a430 */
void nvic_set_priority_53a430(int16_t irq, uint32_t priority)
{
    if (irq >= 0) {
        ((volatile uint8_t *)NVIC_IPR_BASE)[irq] = (uint8_t)(priority << 4);
    } else {
        ((volatile uint8_t *)SCB_SHPR_BASE)[((uint32_t)(int32_t)irq & 0xfu) - 4u] =
            (uint8_t)(priority << 4);
    }
}

/* 0x53a454: an input row with an IRQ direction and a handler is also
 * armed on interrupt channel 0. The pin's mask is built and then
 * overwritten by the enabled-status read before being cleared, as in stock. */
int32_t board_gpio_table_init_53a454(const void *table, uint32_t rows)
{
    const g2_gpio_row_t *row = (const g2_gpio_row_t *)table;

    if (row == 0 || rows == 0u)
        return -1;
    for (uint32_t i = 0; i < rows; i++) {
        if (row[i].mode == G2_GPIO_MODE_OUTPUT) {
            (void)am_hal_gpio_pinconfig_480f0c(row[i].pin, g2_gpio_pincfg_output);
            (void)g2_gpio_hal_write(row[i].pin, row[i].level == 1u);
        } else if (row[i].mode == G2_GPIO_MODE_INPUT) {
            uint32_t config = (g2_gpio_pincfg_input & ~0xc0u) |
                              (((uint32_t)row[i].int_dir & 3u) << 6);
            (void)am_hal_gpio_pinconfig_480f0c(row[i].pin, config);
            if (row[i].int_dir != 0u && row[i].handler != 0) {
                uint32_t pin = row[i].pin;
                uint32_t mask[GPIO_MASK_WORDS];
                audio_uart_lv_memzero_48949c(mask, sizeof mask);
                mask[pin >> 5] = 1u << (pin & 0x1fu);
                (void)am_hal_gpio_interrupt_status_get_4812f6(GPIO_INT_CHANNEL_0, true, mask);
                (void)am_hal_gpio_interrupt_clear_481468(GPIO_INT_CHANNEL_0, mask);
                (void)audio_ble_hci_radio_register_48162c(GPIO_INT_CHANNEL_0, pin,
                                                          (const void *)row[i].handler, 0u);
                (void)audio_ble_hci_radio_pin_mask_4810b0(GPIO_INT_CHANNEL_0,
                                                          GPIO_INT_CTRL_INDV_ENABLE, &pin);
                nvic_set_priority_53a430(g2_gpio_bank_irq_78d6cc[row[i].pin >> 5],
                                         GPIO_IRQ_PRIORITY);
                nvic_enable_irq_53a414(g2_gpio_bank_irq_78d6cc[row[i].pin >> 5]);
            }
        } else if (row[i].mode == G2_GPIO_MODE_DISABLED) {
            (void)am_hal_gpio_pinconfig_480f0c(row[i].pin, g2_gpio_pincfg_disabled);
        }
    }
    return 0;
}

/* 0x53a590 */
int32_t hal_gpio_input_get_53a590(uint32_t pin, uint8_t *level)
{
    uint32_t value = 0u;

    if (audio_uart_pin_read(pin, GPIO_READ_INPUT, &value) != 0u)
        return -1;
    *level = value == 1u ? 1u : 0u;
    return 0;
}

/* 0x53a5e0: GPIO0_001F (IRQ 56), vector slot 0x438120: read, clear, service. */
void am_gpio0_001f_isr_53a5e0(void)
{
    uint32_t status;

    (void)am_hal_gpio_interrupt_irq_status_get_481574(
        (uint32_t)(int32_t)g2_gpio_bank_irq_78d6cc[0], false, &status);
    (void)am_hal_gpio_interrupt_irq_clear_4815f2(
        (uint32_t)(int32_t)g2_gpio_bank_irq_78d6cc[0], status);
    (void)am_hal_gpio_interrupt_service_4816c6(
        (uint32_t)(int32_t)g2_gpio_bank_irq_78d6cc[0], status);
}

/* 0x53a606: GPIO0_203F (IRQ 57), vector slot 0x438124: read, clear, service. */
void am_gpio0_203f_isr_53a606(void)
{
    uint32_t status;

    (void)am_hal_gpio_interrupt_irq_status_get_481574(
        (uint32_t)(int32_t)g2_gpio_bank_irq_78d6cc[1], false, &status);
    (void)am_hal_gpio_interrupt_irq_clear_4815f2(
        (uint32_t)(int32_t)g2_gpio_bank_irq_78d6cc[1], status);
    (void)am_hal_gpio_interrupt_service_4816c6(
        (uint32_t)(int32_t)g2_gpio_bank_irq_78d6cc[1], status);
}

/* 0x53a62c: GPIO0_405F (IRQ 58), vector slot 0x438128: read, clear, service. */
void am_gpio0_405f_isr_53a62c(void)
{
    uint32_t status;

    (void)am_hal_gpio_interrupt_irq_status_get_481574(
        (uint32_t)(int32_t)g2_gpio_bank_irq_78d6cc[2], false, &status);
    (void)am_hal_gpio_interrupt_irq_clear_4815f2(
        (uint32_t)(int32_t)g2_gpio_bank_irq_78d6cc[2], status);
    (void)am_hal_gpio_interrupt_service_4816c6(
        (uint32_t)(int32_t)g2_gpio_bank_irq_78d6cc[2], status);
}
