/*
 * Forced-include target adapter for compiling exact CMSIS-FreeRTOS cmsis_os2.c
 * without an unauthenticated G2 device header or RTE_Components.h.
 */

#ifndef OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_TARGET_H
#define OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_TARGET_H

#include <stdint.h>

/*
 * CMSIS 5.9 predates Clang's Cortex-M55 __ARM_ARCH_8_1M_MAIN__ spelling.
 * Define the compatible Armv8-M Mainline feature before cmsis_compiler.h is
 * parsed so __get_BASEPRI is provided and IRQ_Context matches the stock G2
 * IPSR/PRIMASK/BASEPRI sequence.
 */
#if defined(__ARM_ARCH_8_1M_MAIN__) && !defined(__ARM_ARCH_8M_MAIN__)
#define __ARM_ARCH_8M_MAIN__ 1
#endif

/*
 * Only osKernelInitialize needs the device-header NVIC surface.  Keep it as
 * an unresolved declaration because this constructor tranche does not retain
 * that function and the exact G2 device/RTE binding is not authenticated.
 */
#ifndef SVCall_IRQn
#define SVCall_IRQn (-5)
#endif
void NVIC_SetPriority(int32_t interrupt_number, uint32_t priority);

#endif /* OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_TARGET_H */
