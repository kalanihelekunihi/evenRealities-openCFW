#include <stdint.h>

/* Shared manager record at native RAM 0x200036fc: initialised .data pointer
 * table to the KVDB default records. Evidence (Fix 56): stk12 under Renode,
 * 0x200036fc.. = 0 at t=0 and at t=0.05 s = 2000380c 200037e0 200037c8
 * 20003818 200037fc 20003824 20003808 200037bc (record map: service_kvdb.c).
 * Zero pointers here made SVC_Settings_Init copy from address 0, so 0x09
 * status lost battery/brightness fields. */
extern char g2_kvdb_time_record[], g2_kvdb_setting_record[], g2_kvdb_ring_record[],
            g2_kvdb_time_format_record[], g2_kvdb_temperature_unit_record[],
            g2_kvdb_universal_setting_record[], audio_settings_terminal_record[],
            g2_kvdb_als_scale_record[];
void *audio_settings_manager_storage[8]
    __attribute__((section(".g2.ram.settings_manager_storage"),used,aligned(4))) = {
    g2_kvdb_time_record, g2_kvdb_setting_record, g2_kvdb_ring_record,
    g2_kvdb_time_format_record, g2_kvdb_temperature_unit_record,
    g2_kvdb_universal_setting_record, audio_settings_terminal_record,
    g2_kvdb_als_scale_record,
};

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
