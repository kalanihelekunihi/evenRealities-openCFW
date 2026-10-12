#include <stdint.h>

/* Three complete native table callbacks, 0x31635c, 0x3163ac, 0x316594.
 * Each loads an externally initialized live function pointer and either
 * returns with R0=context or jumps to the target with R0=context and R1
 * holding that loaded pointer. The pointed-to implementation and pointer
 * producer remain genuine runtime contracts. */
typedef uint32_t (*opencfw_em9305_indirect_callback)(uintptr_t,uintptr_t);
static uint32_t dispatch(uintptr_t context,uintptr_t slot)
{
    uintptr_t target=*(volatile uint32_t *)slot;
    if (target==0u) return (uint32_t)context;
    return ((opencfw_em9305_indirect_callback)target)(context,target);
}
uint32_t opencfw_em9305_mode_callback_31635c(uintptr_t context,
                                               uintptr_t table_cell)
{(void)table_cell;return dispatch(context,0x8051f4u);}
uint32_t opencfw_em9305_mode_callback_3163ac(uintptr_t context,
                                               uintptr_t table_cell)
{(void)table_cell;return dispatch(context,0x8052c4u);}
uint32_t opencfw_em9305_mode_callback_316594(uintptr_t context,
                                               uintptr_t table_cell)
{(void)table_cell;return dispatch(context,0x8056d8u);}
