/* IAR DLIB C11 Annex K runtime-constraint call, native 0x4d40a0..0x4d40bb
 * (literal 0x4d40bc, string 0x4d40c0). The original is IAR DLIB; this is a
 * clean freestanding equivalent. Calls the handler installed at RAM 0x20074f10
 * with (message, NULL, ERANGE = 34), or aborts through 0x541b74 when none is
 * set (g2_main_formatter_abort in system/log/full-formatter). Returns 34. The
 * bootloader copy is opencfw_boot_constraint_dispatch_core (boot 0x422590). */
#include <stdint.h>
#include <stddef.h>

#define CONSTRAINT_ERRNO 34u

typedef void (*g2_constraint_handler_t)(const char *message, void *ptr, uint32_t error);

extern g2_constraint_handler_t g2_iar_constraint_handler; /* RAM 0x20074f10 */
extern void g2_main_formatter_abort(void);                /* 0x541b74 */

static const char bad_message[] = "constraint handler: bad message"; /* ROM 0x4d40c0 */

uint32_t constraint_handler_call_4d40a0(const char *message)
{
    if (message == NULL)
        message = bad_message;
    g2_constraint_handler_t handler = g2_iar_constraint_handler;
    if (handler == NULL)
        g2_main_formatter_abort();
    else
        handler(message, NULL, CONSTRAINT_ERRNO);
    return CONSTRAINT_ERRNO;
}
