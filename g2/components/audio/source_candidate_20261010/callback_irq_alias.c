/* The callback's saved-PRIMASK helper and UART's saved-PRIMASK helper are
 * Apollo 0x473940. Export both names at the exact source entry. */
#include "../uart_power_composition_offline/power.c"

__asm__(".global callback_save_disable_irq\n"
        ".set callback_save_disable_irq, uart_save_irq\n");
