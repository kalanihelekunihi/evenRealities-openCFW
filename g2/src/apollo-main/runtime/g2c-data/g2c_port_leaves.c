/* g2c: small port leaves required by upstream units (wave 2).
 * Profile g2-apollo-main-1. */
#include <stdint.h>

#define G2C_SYST_LOAD (*(volatile uint32_t *)0xE000E014u)
#define G2C_SYST_VAL  (*(volatile uint32_t *)0xE000E018u)

/* Evidence: upstream cmsis-freertos CMSIS/RTOS2/FreeRTOS/Source/os_systick.c
 * OS_Tick_GetInterval/GetCount (SysTick LOAD/VAL); stock FreeRTOS port uses SysTick. */
uint32_t OS_Tick_GetInterval(void) { return G2C_SYST_LOAD + 1u; }
uint32_t OS_Tick_GetCount(void)    { uint32_t load = G2C_SYST_LOAD; return load - G2C_SYST_VAL; }

/* Evidence: upstream easylogger/easylogger/port/elog_port.c elog_port_deinit
 * is empty template ("add your code here"); no stock body identified. */
void elog_port_deinit(void) {}
