/* Stock Main 0x47df28: persist the 16-byte TPS1 tracepoint state record. */
#include <stdint.h>

extern volatile uint32_t audio_tracepoint_session_generation_20074ad4;
extern volatile uint32_t audio_tracepoint_next_sequence_20004188;
extern uint32_t audio_tracepoint_crc32_48ecae(const uint8_t *,uint32_t);
extern void *audio_tracepoint_file_open_474550(const char *,const char *);
extern int32_t audio_tracepoint_file_write_474682(const void *,uint32_t,uint32_t,void *);
extern int32_t audio_file_close(void *);

static void le32(uint8_t *out,uint32_t value) {
    out[0]=(uint8_t)value;out[1]=(uint8_t)(value>>8);
    out[2]=(uint8_t)(value>>16);out[3]=(uint8_t)(value>>24);
}

int32_t audio_tracepoint_write_state_47df28(void) {
    uint8_t record[16]={'T','P','S','1',0,0,0,0,0,0,0,0,0,0,0,0};
    le32(record+4u,audio_tracepoint_session_generation_20074ad4);
    le32(record+8u,audio_tracepoint_next_sequence_20004188);
    le32(record+12u,audio_tracepoint_crc32_48ecae(record,12u));
    void *handle=audio_tracepoint_file_open_474550("/log/tp/state.bin","wb");
    if(handle==0) return -5;
    int32_t written=audio_tracepoint_file_write_474682(record,1u,16u,handle);
    (void)audio_file_close(handle);
    return written==16 ? 0 : -5;
}
