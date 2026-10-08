#include <stdint.h>

/* Stock 0x41583c stores its input through literal pointer 0x200270cc. */
void apollo510_set_external_mode(uint32_t value)
{
    *(volatile uint32_t *)0x200270ccu = value;
}
