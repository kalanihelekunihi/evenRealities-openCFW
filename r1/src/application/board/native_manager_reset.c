/* Stock 0x381a4: architectural reset after caller-side trace capture. */
#include "nrf.h"
__attribute__((noreturn)) void r1_manager_system_reset(void)
{
 __NVIC_SystemReset();
}
