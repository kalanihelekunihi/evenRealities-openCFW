/* Stock Main 0x47df8a: restore a valid TPS1 state record. */
#include <stdint.h>

extern volatile uint32_t audio_tracepoint_session_generation_20074ad4;
extern volatile uint32_t audio_tracepoint_next_sequence_20004188;
extern uint32_t audio_tracepoint_crc32_48ecae(const uint8_t *,uint32_t);
extern void *audio_file_open(const char *,const char *);
extern uint32_t audio_file_read(void *,uint32_t,uint32_t,void *);
extern int32_t audio_file_close(void *);

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

void audio_tracepoint_read_state_47df8a(void) {
    uint8_t record[16];
    void *handle=audio_file_open("/log/tp/state.bin","rb");
    if(handle==0) return;
    uint32_t read=audio_file_read(record,1u,16u,handle);
    (void)audio_file_close(handle);
    if(read!=16u || word(record)!=0x31535054u ||
       word(record+12u)!=audio_tracepoint_crc32_48ecae(record,12u)) return;
    audio_tracepoint_session_generation_20074ad4=word(record+4u);
    uint32_t next=word(record+8u);
    audio_tracepoint_next_sequence_20004188=next<2u ? 1u : next;
}
