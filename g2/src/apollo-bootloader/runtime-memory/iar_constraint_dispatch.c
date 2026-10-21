/* SPDX-License-Identifier: MIT
 * IAR C11 runtime constraint dispatcher at native 0x422590. The ambient
 * high-word return register is handled by iar_constraint_dispatch_entry.S.
 */
#include <stdint.h>

extern void opencfw_format_abort_contract(void);

typedef void (*opencfw_constraint_handler_t)(const char *, void *, uint32_t);

uint32_t opencfw_boot_constraint_dispatch_core(const char *message)
{
    static const char bad_message[] = "constraint handler: bad message";
    if (message == 0)
        message = bad_message;
    opencfw_constraint_handler_t handler =
        *(opencfw_constraint_handler_t volatile *)(uintptr_t)UINT32_C(0x20027190);
    if (handler == 0)
        opencfw_format_abort_contract();
    else
        handler(message, 0, 34u);
    return 34u;
}
