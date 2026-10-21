/* Stock Main tracepoint delete filename normalizer at 0x5ede30. */
#include <stdint.h>
extern uint32_t audio_tracepoint_role_char_5edadc(void);
extern uint32_t audio_uart_ring_parse_uint_48d874(const char *,const char **,uint32_t);
extern int32_t audio_tracepoint_resolve_file_path_5eddf6(char *,uint32_t *);
extern int32_t audio_tracepoint_parse_sequence_5edaf0(const char *,uint32_t *);
extern void audio_tracepoint_format_file_path_5edba2(char *,uint32_t,uint32_t);
int32_t audio_tracepoint_validate_file_name_5ede30(const char *name,char *output,
                                                     uint32_t capacity)
{
    uint32_t sequence=0;
    const char *end=0;
    if (name==0 || output==0 || capacity==0u)
        return -1;
    uint8_t role=(uint8_t)audio_tracepoint_role_char_5edadc();
    if (name[0]=='R' || name[0]=='L') {
        if ((uint8_t)name[0]!=role || name[1]!=':')
            return -1;
        name+=2;
    }
    if (name[0]=='t') {
        sequence=audio_uart_ring_parse_uint_48d874(name+1,&end,10u);
        if (end==0 || *end!='\0' || sequence==0u)
            return -1;
    } else if (audio_tracepoint_resolve_file_path_5eddf6((char *)name,&sequence)==0 &&
               audio_tracepoint_parse_sequence_5edaf0(name,&sequence)==0) {
        return -1;
    }
    audio_tracepoint_format_file_path_5edba2(output,capacity,sequence);
    return 0;
}
