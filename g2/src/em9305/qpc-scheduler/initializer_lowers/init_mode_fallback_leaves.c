#include <stdint.h>

/* Three native return-delay byte stores at 0x32cac4/cc/d4. */
uint32_t opencfw_em9305_mode_event_32cac4(uintptr_t context)
{ *(volatile uint8_t *)(context+12u)=0x28u;return (uint32_t)context; }
uint32_t opencfw_em9305_mode_event_32cacc(uintptr_t context)
{ *(volatile uint8_t *)(context+12u)=0x1eu;return (uint32_t)context; }
uint32_t opencfw_em9305_mode_event_32cad4(uintptr_t context)
{ *(volatile uint8_t *)(context+12u)=0x30u;return (uint32_t)context; }
