/* The generic action/enable callback dispatcher at 0x480313 is the already
 * reconstructed uart_group_control entry. Its function body narrows the two
 * scalars and uses the shared callback slot for all groups. */
#include "../../hal/uart/uart-group-power/providers.c"

__asm__(".global stock_dispatch\n"
        ".set stock_dispatch, uart_group_control\n");
