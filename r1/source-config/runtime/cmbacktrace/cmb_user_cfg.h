#ifndef R1_SOURCE_CMB_INIT_CFG_H
#define R1_SOURCE_CMB_INIT_CFG_H
#include <stdint.h>
#define CMB_USING_OS_PLATFORM
#define CMB_OS_PLATFORM_TYPE CMB_OS_PLATFORM_FREERTOS
#define CMB_CPU_PLATFORM_TYPE CMB_CPU_ARM_CORTEX_M4
#define CMB_USING_DUMP_STACK_INFO
#define CMB_PRINT_LANGUAGE CMB_PRINT_LANGUAGE_ENGLISH
#define CMB_NAME_MAX 20
#define CMB_CALL_STACK_MAX_DEPTH 32
#define CMB_DUMP_STACK_DEPTH_SIZE 16
#define CMB_CSTACK_BLOCK_START r1_cmb_stack_start
#define CMB_CSTACK_BLOCK_END r1_cmb_stack_end
#define CMB_CODE_SECTION_START r1_cmb_code_start
#define CMB_CODE_SECTION_END r1_cmb_code_end
extern void r1_retained_log_printf_sink(const char *,...);
#define cmb_println(...) r1_retained_log_printf_sink(__VA_ARGS__)
#endif
