/*
 * Clang include adapter for the authenticated FreeRTOS-Kernel V10.5.1
 * IAR/ARM_CM55_NTZ/non_secure portable layer.
 *
 * The common upstream header is compiler-neutral for this C-only constructor
 * closure.  The IAR leaf adds only __root, two IAR diagnostics, the MVE
 * configuration check, and the interrupt enable/disable aliases.  Re-express
 * those usable aliases here without inventing an unresolved configENABLE_MVE
 * value or exposing IAR syntax to Clang.
 */

#ifndef OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_PORTMACRO_H
#define OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_PORTMACRO_H

#include "portmacrocommon.h"

#define portARCH_NAME                "Cortex-M55"
#define portDONT_DISCARD             __attribute__((used))
#define portDISABLE_INTERRUPTS()     ulSetInterruptMask()
#define portENABLE_INTERRUPTS()      vClearInterruptMask(0)

#endif /* OPEN_CFW_CMSIS_FREERTOS_CONSTRUCTOR_PORTMACRO_H */
