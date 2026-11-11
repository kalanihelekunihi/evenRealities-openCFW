#ifndef R1_NATIVE_DEMO_RESET_CONFIG_H
#define R1_NATIVE_DEMO_RESET_CONFIG_H
/* Keep the kernel's sibling vendor configuration, except for reset and interrupt policy.
 * Locked R1 Gh3x2xDemoInit calls GH3X2X_SoftReset at 0x2d9be. */
#include "kernel/gh_demo_config.h"
#undef __SUPPORT_HARD_RESET_CONFIG__
#define __SUPPORT_HARD_RESET_CONFIG__ (0)
/* Initialized stock mode byte at 0x20007af1 is 1. Stock interrupt
 * processing omits the external-interrupt callback gate. */
#undef __INTERRUPT_PROCESS_MODE__
#define __INTERRUPT_PROCESS_MODE__ (__POLLING_INT_PROCESS_MODE__)
#endif
