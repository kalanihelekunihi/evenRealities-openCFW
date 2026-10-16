/* Stock Main tracepoint filename sequence parser at 0x5edaf0. */
#include <stdint.h>
extern uint32_t g2_log_candidate_module_length(const char *);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern int32_t audio_uart_font_path_compare(const char *,const char *);
extern uint32_t audio_uart_ring_parse_uint_48d874(const char *,const char **,uint32_t);
static const char extension[]=".bin";
int32_t audio_tracepoint_parse_sequence_5edaf0(const char *name,uint32_t *sequence)
{
    uint32_t length;
    const char *end=0;
    uint32_t value;
    if (name==0 || sequence==0)
        return 0;
    length=g2_log_candidate_module_length(name);
    if (length<=7u || audio_ble_hci_vendor_compare_44b610(name,"tp_",3u)!=0 ||
        audio_uart_font_path_compare(name+length-4u,extension)!=0)
        return 0;
    value=audio_uart_ring_parse_uint_48d874(name+3u,&end,10u);
    if (end==0 || end!=name+length-4u || value==0u)
        return 0;
    *sequence=value;
    return 1;
}
