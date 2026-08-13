/* R1 integration configuration for the authenticated Armink provider. */
#ifndef OPENR1_CMB_USER_CFG_H
#define OPENR1_CMB_USER_CFG_H

#include "openr1_cmbacktrace_port.h"

#define CMB_USING_OS_PLATFORM
#define CMB_OS_PLATFORM_TYPE CMB_OS_PLATFORM_FREERTOS
#define CMB_CPU_PLATFORM_TYPE CMB_CPU_ARM_CORTEX_M4
#define CMB_USING_DUMP_STACK_INFO
#define CMB_PRINT_LANGUAGE CMB_PRINT_LANGUAGE_ENGLISH

/* Values recovered from the R1 2.2.6.0009 image. */
#define CMB_NAME_MAX 20
#define CMB_CALL_STACK_MAX_DEPTH 32
#define CMB_DUMP_STACK_DEPTH_SIZE 16

#define cmb_println(...) openr1_cmbacktrace_log(__VA_ARGS__)

#endif /* OPENR1_CMB_USER_CFG_H */
