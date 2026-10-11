/* Stock 0x42a030 selector-24 callback: BX LR preserves incoming registers. */
#include <stdint.h>

__attribute__((naked)) uint32_t event_a_transition_sequence_24(uint32_t target_state,
    uint32_t current_state, uint32_t target_ton_state, uint32_t current_ton_state)
{
    __asm__ volatile("bx lr");
}

/* Stock selector-25 and selector-26 are separate two-byte BX LR bodies at
 * 0x42a032 and 0x42a034. Keep distinct relocatable symbols so the initialized
 * callback table retains three independently placeable entry points. */
__attribute__((naked)) uint32_t event_a_transition_sequence_25(uint32_t target_state,
    uint32_t current_state, uint32_t target_ton_state, uint32_t current_ton_state)
{
    __asm__ volatile("bx lr");
}

__attribute__((naked)) uint32_t event_a_transition_sequence_26(uint32_t target_state,
    uint32_t current_state, uint32_t target_ton_state, uint32_t current_ton_state)
{
    __asm__ volatile("bx lr");
}
