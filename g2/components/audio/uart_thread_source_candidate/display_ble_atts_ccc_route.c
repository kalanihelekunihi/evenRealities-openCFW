/* Apollo ATT CCC route: 0x52bcea, 0x52c5f2, 0x52c628. */
#include <stdint.h>

extern volatile uint8_t audio_ble_atts_ccc_runtime_20073b00[];
extern uint8_t audio_ble_dm_sec_level_4b71b2(uint8_t);
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,...);

static const char error_label[]="ERR";
static const char warn_label[]="WARN";
static const char info_label[]="INFO";
static const char att_label[]="ATT";
static const char hci_label[]="HCI";
static const char invalid[]="Invalid connId in attsCccGetTbl: %d";
static const char function_name[]="attsCccGetTbl";
static const char path[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_ccc.c";

uint32_t audio_ble_atts_ccc_get_table_52bcea(uint8_t connection)
{
    if (connection != 0u) {
        const volatile uint32_t *slot=(const volatile uint32_t *)(const void *)
            (audio_ble_atts_ccc_runtime_20073b00 + ((uint32_t)connection-1u)*4u);
        return *slot;
    }
    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
        audio_l2c_strncmp(warn_label,error_label,3u) != 0) {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_l2c_strncmp(warn_label,warn_label,4u) != 0) {
            if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                audio_l2c_strncmp(warn_label,info_label,4u) != 0) {
                if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u) {
                    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                        audio_l2c_strncmp(att_label,hci_label,3u) != 0)
                        audio_ble_wsf_trace(warn_label,invalid,0u);
                } else if (audio_log_flags() & 2u) {
                    audio_log_extended(4u,att_label,path,function_name,0x85u,
                                       invalid,0u);
                }
            } else if (audio_log_flags() & 2u) {
                audio_log_extended(3u,att_label,path,function_name,0x85u,
                                   invalid,0u);
            }
        } else if (audio_log_flags() & 2u) {
            audio_log_extended(2u,att_label,path,function_name,0x85u,invalid,0u);
        }
    } else if (audio_log_flags() & 2u) {
        audio_log_extended(1u,att_label,path,function_name,0x85u,invalid,0u);
    }
    return 0u;
}

uint16_t audio_ble_atts_ccc_get_52c5f2(uint8_t connection,uint8_t route)
{
    uint32_t table=audio_ble_atts_ccc_get_table_52bcea(connection);
    if (table==0u) return 0u;
    const volatile uint16_t *slot=(const volatile uint16_t *)(uintptr_t)
        (table+(uint32_t)route*2u);
    return *slot;
}

uint32_t audio_ble_adv_route_ready_52c628(uint8_t connection,uint8_t route)
{
    uint8_t security=audio_ble_dm_sec_level_4b71b2(connection);
    uint32_t limits=*(const volatile uint32_t *)(const void *)
        (audio_ble_atts_ccc_runtime_20073b00+0x0cu);
    uint8_t required=*(const volatile uint8_t *)(uintptr_t)
        (limits+(uint32_t)route*6u+4u);
    if (security<required) return 0u;
    return audio_ble_atts_ccc_get_52c5f2(connection,route);
}
