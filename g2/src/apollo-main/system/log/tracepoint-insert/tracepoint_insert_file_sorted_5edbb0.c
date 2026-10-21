/* Native tracepoint_insert_file_sorted 0x5edbb0. */
#include <stdint.h>

extern uint8_t audio_tracepoint_file_inventory[0x88];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="tp.setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function[]="tracepoint_insert_file_sorted";
static const char full[]="tracepoint file list full, drop seq=%u size=%u";
static const char full_short[]="[tp.setting]tracepoint file list full, drop seq=%u size=%u";

void audio_tracepoint_insert_file_sorted_5edbb0(uint32_t sequence,uint32_t size) {
    uint32_t *entries=(uint32_t *)(void *)audio_tracepoint_file_inventory;
    uint32_t *count=(uint32_t *)(void *)(audio_tracepoint_file_inventory+0x80u);
    uint32_t *total=(uint32_t *)(void *)(audio_tracepoint_file_inventory+0x84u);
    uint32_t at=*count;
    if(at<16u) {
        while(at!=0u && sequence<entries[(at-1u)*2u]) {
            entries[at*2u]=entries[(at-1u)*2u];
            entries[at*2u+1u]=entries[(at-1u)*2u+1u];
            at--;
        }
        entries[at*2u]=sequence;
        entries[at*2u+1u]=size;
        *count+=1u;
        *total+=size;
    } else {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x6eu,full,sequence,size);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08800000u,full_short,full_short,sequence,size);
    }
}
