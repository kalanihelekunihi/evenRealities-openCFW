/* Native assertion/logging trees of 0x4b4eee, 0x534f14, 0x52c928.
 * Diagnostic strings are authenticated native literals; the level cell is
 * live product RAM 0x2007502f. */
#include <stdint.h>

extern volatile uint8_t audio_ble_trace_level_cell;
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t); /* 0x44b610 bounded strncmp */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...); /* 0x52a63c */

static const char warn_text[]="WARN";
static const char err_text[]="ERR";
static const char info_text[]="INFO";
static const char att_text[]="ATT";
static const char hci_text[]="HCI";
static const char att_main_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\att_main.c";
static const char atts_main_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_main.c";
static const char atts_csf_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_csf.c";
static const char ccb_name[]="attCcbByConnId";
static const char reg_name[]="attsCcbByConnId";
static const char csf_name[]="attsCsfIsClientChangeAware";
static const char ccb_message[]="Invalid connId in attCcbByConnId: %d";
static const char reg_zero_message[]="Invalid connId in attsCcbByConnId: %d, slot: %d";
static const char reg_invalid_message[]="atts ccb not in use: %d";
static const char csf_message[]="Invalid connId in attsCsfIsClientChangeAware: %d, handle: %d";

static uint32_t cmp(const char *a,const char *b,uint32_t n) {
    return (uint32_t)audio_ble_hci_vendor_compare_44b610(a,b,n);
}
static void log_at(uint8_t level,const char *path,const char *name,
                   uint32_t line,const char *message,uint8_t mode,
                   uint32_t connection,uint32_t registration) {
    if((audio_log_flags()&2u)==0u)return;
    if(mode==0u)
        audio_log_extended(level,att_text,path,name,line,message,0u);
    else if(mode==1u)
        audio_log_extended(level,att_text,path,name,line,message,0u,registration);
    else audio_log_extended(level,att_text,path,name,line,message,connection);
}
static void trace_at(const char *message,uint8_t mode,
                     uint32_t connection,uint32_t registration) {
    if(mode==0u)audio_ble_wsf_trace(warn_text,message,0u);
    else if(mode==1u)audio_ble_wsf_trace(warn_text,message,0u,registration);
    else audio_ble_wsf_trace(warn_text,message,connection);
}
static void assert_path(const char *path,const char *name,
                        uint32_t line,const char *message,uint8_t mode,
                        uint32_t connection,uint32_t registration) {
    /* Exactly the four repeated policy reads and short-circuit compares
     * emitted by the native Cordio assertion macro. */
    if(audio_ble_trace_level_cell!=0u && cmp(warn_text,err_text,3u)==0u) {
        log_at(1u,path,name,line,message,mode,connection,registration);
        return;
    }
    if(audio_ble_trace_level_cell!=0u && cmp(warn_text,warn_text,4u)==0u) {
        log_at(2u,path,name,line,message,mode,connection,registration);
        return;
    }
    if(audio_ble_trace_level_cell!=0u && cmp(warn_text,info_text,4u)==0u) {
        log_at(3u,path,name,line,message,mode,connection,registration);
        return;
    }
    if(audio_ble_trace_level_cell==0u) {
        if(audio_ble_trace_level_cell==0u || cmp(att_text,hci_text,3u)!=0u)
            trace_at(message,mode,connection,registration);
    } else log_at(4u,path,name,line,message,mode,connection,registration);
}

uint8_t *audio_ble_att_ccb_zero_assert(void) {
    assert_path(att_main_path,ccb_name,0x13fu,ccb_message,0u,0u,0u);
    return 0;
}
uint8_t *audio_ble_att_registration_invalid(uint8_t connection,uint8_t registration) {
    if(connection==0u)
        assert_path(atts_main_path,reg_name,0x25cu,reg_zero_message,1u,0u,registration);
    else assert_path(atts_main_path,reg_name,0x264u,reg_invalid_message,2u,connection,registration);
    return 0;
}
uint32_t audio_ble_att_zero_connection_assert(uint16_t attribute) {
    assert_path(atts_csf_path,csf_name,0x80u,csf_message,1u,0u,attribute);
    return 0u;
}
