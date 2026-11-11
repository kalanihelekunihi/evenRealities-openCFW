/* Newlib assertions use the existing Nordic fatal-error policy. The SDK
 * assertion record carries file and line; function/expression strings have
 * no fields in that protocol. The fallback remains nonreturning if an
 * application override unexpectedly returns from the fault handler. */
#include <stdint.h>
#include <stddef.h>
#include "app_error.h"
_Static_assert(sizeof(assert_info_t)==8 && offsetof(assert_info_t,line_num)==0 &&
               offsetof(assert_info_t,p_file_name)==4,"Nordic assert record ABI");
_Noreturn void __assert_func(const char *file,int line,const char *function,
                            const char *expression)
{
    (void)function;(void)expression;
    assert_info_t info={.line_num=(uint32_t)line,.p_file_name=(const uint8_t *)file};
    app_error_fault_handler(NRF_FAULT_ID_SDK_ASSERT,0,(uint32_t)(uintptr_t)&info);
    for (;;) {}
}
