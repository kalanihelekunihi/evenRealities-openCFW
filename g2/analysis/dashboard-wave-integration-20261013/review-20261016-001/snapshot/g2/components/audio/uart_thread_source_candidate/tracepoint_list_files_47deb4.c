/* Stock Main 0x47deb4: count and bound tracepoint sequence files. */
#include <stdint.h>

extern void *audio_tracepoint_dir_open_474b02(const char *);
extern void *audio_tracepoint_dir_read_474bb8(void *);
extern int32_t audio_tracepoint_dir_close_474c66(void *);
extern int32_t audio_tracepoint_parse_file_entry_47de18(const void *,uint32_t *);

int32_t audio_tracepoint_list_files_47deb4(uint32_t *summary) {
    summary[0]=0u;
    summary[1]=0xffffffffu;
    summary[2]=0u;
    void *dir=audio_tracepoint_dir_open_474b02("/log/tp");
    if(dir==0) return -5;
    for(;;) {
        const uint8_t *entry=(const uint8_t *)audio_tracepoint_dir_read_474bb8(dir);
        if(entry==0) break;
        if(entry[0x100u]==8u) {
            uint32_t sequence;
            if(audio_tracepoint_parse_file_entry_47de18(entry,&sequence)!=0) {
                summary[0]++;
                if(sequence<summary[1]) summary[1]=sequence;
                if(sequence>summary[2]) summary[2]=sequence;
            }
        }
    }
    (void)audio_tracepoint_dir_close_474c66(dir);
    return 0;
}
