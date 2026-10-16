/* Stock Main 0x47de18: accept tp_<decimal>.bin directory names. */
#include <stdint.h>

extern uint32_t g2_log_module_length(const char *);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern int32_t audio_uart_font_path_compare(const char *,const char *);
extern uint32_t audio_uart_ring_parse_uint_48d874(const char *,const char **,uint32_t);

int32_t audio_tracepoint_parse_file_entry_47de18(const char *name,uint32_t *sequence) {
    uint32_t length=g2_log_module_length(name);
    if(length<8u ||
       audio_ble_hci_vendor_compare_44b610(name,"tp_",3u)!=0 ||
       audio_uart_font_path_compare(name+length-4u,".bin")!=0)
        return 0;
    const char *end=0;
    uint32_t value=audio_uart_ring_parse_uint_48d874(name+3u,&end,10u);
    if(end==0 || end!=name+length-4u) return 0;
    *sequence=value;
    return 1;
}
