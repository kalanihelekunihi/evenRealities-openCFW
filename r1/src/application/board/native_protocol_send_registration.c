/* Stock0x83448: a null registration fails without clearing the previous hook.
 * The public C caller consumes the return/slot, not caller-saved registers. */
#include <stdint.h>
extern volatile uintptr_t r1_protocol_send_hook;
uint32_t r1_protocol_send_callback_set(uintptr_t callback)
{
    if(!callback)return UINT32_MAX;
    r1_protocol_send_hook=callback;
    return 0;
}
