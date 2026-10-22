/* SPDX-License-Identifier: MIT
 * Touch (PSoC 4000T) product platform glue: SysTick gesture timebase, host
 * I2C slave (SCB1, 7-bit address 0x0C, IRQ7), application PM registration,
 * hold-threshold normaliser and the DFU mailbox reset. Reconstructed from
 * official 2.2.6.10 firmware_touch.bin, native 0x35E4..0x3700, 0x3CA4,
 * 0x3EE8 and 0x7E30. Not byte-identical by construction.
 */
#include <stdint.h>
#include <stddef.h>
#include "cy_scb_i2c.h"
#include "application.h"
#include "../calibration/calibration.h"
#include "../pm-callbacks/callbacks.h"

typedef void (*g2_touch_isr)(void);

extern uint32_t Cy_SysInt_Init(const g2_touch_sysint_config *config, g2_touch_isr handler); /* 0xA2A8 */
extern void Cy_SysTick_Init(uint32_t clockSource, uint32_t interval);                    /* 0xA650 */
extern g2_touch_isr Cy_SysTick_SetCallback(uint32_t number, g2_touch_isr function);       /* 0xA6A8 */
extern void app_event(uint32_t events);                                                  /* 0x3700 */
extern touch_pm_callback touch_reset_app_pm_descriptor;                                  /* RAM 0x200004CC */
extern __attribute__((noreturn)) void touch_reset_boundary(void);                       /* 0x7E14 NVIC_SystemReset */

#define I2C_CTX ((cy_stc_scb_i2c_context_t *)G2_TOUCH_I2C_CONTEXT)
#define NVIC_ISER (*(volatile uint32_t *)0xE000E100u)
#define NVIC_ICPR (*(volatile uint32_t *)0xE000E280u)

/* Generated SCB1 slave configuration (ROM 0xB374, 24 B):
 * slave, RX/TX FIFO, address 0x0C, mask 0xFE, wake-from-sleep. */
static const cy_stc_scb_i2c_config_t touch_i2c_config = {
    .i2cMode = CY_SCB_I2C_SLAVE,
    .useRxFifo = true,
    .useTxFifo = true,
    .slaveAddress = 0x0Cu,
    .slaveAddressMask = 0xFEu,
    .acceptAddrInFifo = false,
    .ackGeneralAddr = false,
    .enableWakeFromSleep = true,
};

/* SCB1 interrupt: IRQ7, priority 2 (ROM 0xB0E8). */
static const g2_touch_sysint_config touch_scb1_irq_config = {7, 2u};

/* Stock 0x000035E4 (touch_storage_02e4_increment) - SysTick callback slot 0. */
void touch_storage_02e4_increment(void)
{
    G2_TOUCH_GESTURE_TICKS++;
}

/* Stock 0x00003624 (touch_platform_0324_configure) - SCB1 I2C ISR. */
void touch_platform_0324_configure(void)
{
    Cy_SCB_I2C_SlaveInterrupt(SCB1, I2C_CTX);
}

/* Stock 0x00003638 (touch_platform_0338_install) - SysTick on clk_lf
 * (source 0), reload 40; the counter restarts at `start`. */
void touch_platform_0338_install(uint32_t start)
{
    G2_TOUCH_GESTURE_TICKS = start;
    Cy_SysTick_Init(0u, 40u);
    (void)Cy_SysTick_SetCallback(0u, touch_storage_02e4_increment);
}

/* Stock 0x00003658 (touch_platform_0358_sample) - gesture state from the
 * saved hold parameter (record 0x200009D0 + 6). */
void touch_platform_0358_sample(void)
{
    uint16_t hold = G2_TOUCH_SAVED_HOLD;
    touch_gesture_initialize(G2_TOUCH_GESTURE_STATE, &hold);
}

/* Stock 0x00003678 (i2c_slave_init) */
void i2c_slave_init(void)
{
    (void)Cy_SCB_I2C_Init(SCB1, &touch_i2c_config, I2C_CTX);
    (void)Cy_SysInt_Init(&touch_scb1_irq_config, touch_platform_0324_configure);
    Cy_SCB_I2C_SlaveConfigReadBuf(SCB1, G2_TOUCH_I2C_TX, 16u, I2C_CTX);
    Cy_SCB_I2C_SlaveConfigWriteBuf(SCB1, G2_TOUCH_I2C_RX, 16u, I2C_CTX);
    Cy_SCB_I2C_RegisterEventCallback(SCB1, app_event, I2C_CTX);
    /* NVIC_ClearPendingIRQ / NVIC_EnableIRQ for the constant IRQ7. */
    NVIC_ICPR = 1u << 7;
    NVIC_ISER = 1u << 7;
    Cy_SCB_I2C_Enable(SCB1, I2C_CTX);
}

/* Stock 0x00003CA4 (touch_platform_09a4_start) - register the application
 * DeepSleep descriptor (RAM 0x200004CC, callback 0x3620, order 2). */
void touch_platform_09a4_start(void)
{
    (void)touch_pm_register(&touch_reset_app_pm_descriptor);
}

/* Stock 0x00003EE8 (timeout_default_1000_if_zero) */
void timeout_default_1000_if_zero(uint16_t *hold)
{
    if (hold != NULL && *hold == 0u) {
        *hold = 1000u;
    }
}

/* Stock 0x00007E30 (enter_dfu_mailbox_and_reset) - application id 0/1 into
 * the first RAM byte, then system reset into the resident bootloader. */
void enter_dfu_mailbox_and_reset(uint32_t app)
{
    if (app > 1u) {
        __asm volatile ("bkpt #1");
    }
    G2_TOUCH_DFU_MAILBOX = (uint8_t)app;
    touch_reset_boundary();
}
