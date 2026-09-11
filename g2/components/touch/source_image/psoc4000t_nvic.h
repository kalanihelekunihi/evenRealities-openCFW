/*
 * SPDX-License-Identifier: MIT
 *
 * PSoC 4000T (CY8C4046FNI) Cortex-M0+ external-IRQ vector configuration.
 *
 * This header expresses *silicon* configuration, not firmware content: the
 * IRQ number assigned to each on-chip peripheral is fixed by the PSoC 4000T
 * NVIC wiring and is public in Infineon's `psoc4000t.svd` interrupt list
 * (thirteen external lines, in order: IOSS0-4, SRSS_WDT, SCB0, SCB1,
 * MSCLP_LP, SPCIF, MSCLP, TCPWM0, TCPWM1). It is independent of, and does
 * not encode, any byte from the stock touch firmware image.
 *
 * `g2/docs/research/g2-touch-identity-recovery.md` ("ARMv6-M vector-table
 * shape", finding 4) already cross-checked the shipped image's vector-table
 * *shape* (13 populated external slots, all pointing at one default
 * handler) against this public SVD ordering to identify the part; it does
 * not read peripheral assignment out of the firmware. That means *which*
 * slot number belongs to *which* peripheral is knowable without a board and
 * without the stock image, and is recorded here as an explicit, named,
 * host-tested configuration table (see
 * `tests/test_runtime_touch_nvic_config.py`) instead of the bare positional
 * zeros an unexplained vector array would otherwise be.
 *
 * What remains genuinely hardware-blocked is the runtime MMIO *behavior*
 * each handler would need to perform against a real part (servicing the
 * SCB1 I2C shift register, draining an MSCLP CapSense scan-complete FIFO,
 * and so on) -- see `hardware_validation` in
 * `components/touch/source_image/README.md`. This header does not attempt
 * that; the handlers it names stay minimal/no-op ISRs, exactly as before.
 */
#ifndef OPEN_CFW_TOUCH_PSOC4000T_NVIC_H
#define OPEN_CFW_TOUCH_PSOC4000T_NVIC_H

/*
 * Cortex-M0+ vector-table index of external IRQ0: 16 fixed core exception
 * slots precede it (0 initial SP, 1 Reset, 2 NMI, 3 HardFault, 4-10
 * reserved, 11 SVCall, 12-13 reserved, 14 PendSV, 15 SysTick). This count is
 * architectural (ARMv6-M), not device-specific.
 */
#define OPEN_CFW_TOUCH_CORE_VECTOR_COUNT 16U

/*
 * PSoC 4000T external IRQ assignment, in `psoc4000t.svd` order. Values are
 * the NVIC IRQ number (0-based), not the Cortex-M0+ vector-table index; use
 * OPEN_CFW_TOUCH_VECTOR_INDEX() to convert.
 */
typedef enum open_cfw_touch_psoc4000t_irq {
    OPEN_CFW_TOUCH_IRQ_IOSS0    = 0,  /* GPIO port group 0 */
    OPEN_CFW_TOUCH_IRQ_IOSS1    = 1,  /* GPIO port group 1 */
    OPEN_CFW_TOUCH_IRQ_IOSS2    = 2,  /* GPIO port group 2 */
    OPEN_CFW_TOUCH_IRQ_IOSS3    = 3,  /* GPIO port group 3 */
    OPEN_CFW_TOUCH_IRQ_IOSS4    = 4,  /* GPIO port group 4 */
    OPEN_CFW_TOUCH_IRQ_SRSS_WDT = 5,  /* system-resource subsystem watchdog */
    OPEN_CFW_TOUCH_IRQ_SCB0     = 6,  /* serial communication block 0 */
    OPEN_CFW_TOUCH_IRQ_SCB1     = 7,  /* serial communication block 1 (host I2C) */
    OPEN_CFW_TOUCH_IRQ_MSCLP_LP = 8,  /* CapSense low-power wake */
    OPEN_CFW_TOUCH_IRQ_SPCIF    = 9,  /* SPCIF flash/SROM interface */
    OPEN_CFW_TOUCH_IRQ_MSCLP    = 10, /* CapSense scan complete */
    OPEN_CFW_TOUCH_IRQ_TCPWM0   = 11, /* timer/counter/PWM block 0 */
    OPEN_CFW_TOUCH_IRQ_TCPWM1   = 12, /* timer/counter/PWM block 1 */
    OPEN_CFW_TOUCH_IRQ_COUNT    = 13
} open_cfw_touch_psoc4000t_irq;

/* Cortex-M0+ vector-table index for a given PSoC 4000T external IRQ. */
#define OPEN_CFW_TOUCH_VECTOR_INDEX(irq) \
    (OPEN_CFW_TOUCH_CORE_VECTOR_COUNT + (unsigned)(irq))

/* Total vector-table entries this part's NVIC requires: core + external. */
#define OPEN_CFW_TOUCH_VECTOR_TABLE_LENGTH \
    OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_COUNT)

#endif
