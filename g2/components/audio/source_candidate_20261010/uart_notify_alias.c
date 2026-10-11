/* The UART stream's task notification uses Apollo 0x455dc0.
 * Preserve the independently compared ISR notifier body at that entry. */
#include "../uart_rx_notifier_offline/notify.c"

__asm__(".global offline_notify\n"
        ".set offline_notify, uart_notify_isr\n");
