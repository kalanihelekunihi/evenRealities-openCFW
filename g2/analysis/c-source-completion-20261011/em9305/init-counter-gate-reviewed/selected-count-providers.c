#include <stdint.h>
uint32_t opencfw_em9305_command_count_down_30e48c(void)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805a79u;
 *(volatile uint8_t *)(uintptr_t)0x805a79u=(uint8_t)(count-1u);
 return 0x805a79u;
}
uint32_t opencfw_em9305_init_state_count_down_30e49c(void)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805a76u;
 *(volatile uint8_t *)(uintptr_t)0x805a76u=(uint8_t)(count-1u);return 0x805a76u;
}
