#include <stdint.h>

/* Shared manager record at native RAM 0x200036fc. Native consumers address
 * fields at +0, +4, +0x18 and +0x1c; producer initialization remains open. */
uint32_t audio_settings_manager_storage[8]
    __attribute__((section(".g2.ram.settings_manager_storage"),used,aligned(4)));

__asm__(".global audio_uart_hand_snapshot_context\n"
        ".set audio_uart_hand_snapshot_context,audio_settings_manager_storage\n"
        ".global g2_audio_log_timezone\n"
        ".set g2_audio_log_timezone,audio_settings_manager_storage\n"
        ".global audio_settings_config_previous\n"
        ".set audio_settings_config_previous,audio_settings_manager_storage+4\n"
        ".global audio_settings_als_previous\n"
        ".set audio_settings_als_previous,audio_settings_manager_storage+24\n"
        ".global audio_settings_terminal_previous\n"
        ".set audio_settings_terminal_previous,audio_settings_manager_storage+28\n");
