/* Stock Main tracepoint pathname prefix recognizer at 0x5eddf6. */
#include <stdint.h>
extern uint32_t g2_log_candidate_module_length(const char *);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern int32_t audio_tracepoint_parse_sequence_5edaf0(const char *,uint32_t *);
static const char prefix[]="/log/tp/";
int32_t audio_tracepoint_resolve_file_path_5eddf6(char *path,uint32_t *sequence)
{
    uint32_t length=g2_log_candidate_module_length(prefix);
    if (path==0 || audio_ble_hci_vendor_compare_44b610(path,prefix,length)!=0)
        return 0;
    return audio_tracepoint_parse_sequence_5edaf0(path+length,sequence);
}
