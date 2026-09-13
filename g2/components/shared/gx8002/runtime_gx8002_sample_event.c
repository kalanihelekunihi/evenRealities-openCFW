/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <lvp_app.h>
struct event_state { uint32_t last_vad; uint8_t pending; };
extern struct event_state open_cfw_gx8002_event_state;
extern uint32_t open_cfw_gx8002_event_app[7];
extern int printf(const char *,...);
extern int open_cfw_gx8002_context_lookup(uint32_t,void **,uint32_t *);
extern int open_cfw_gx8002_vad_notify(uint32_t);
extern int open_cfw_gx8002_event_notify(uint32_t);
extern int open_cfw_gx8002_mic_buffer(const uint32_t *,uint32_t,uint32_t,uint32_t *,uint32_t *);
extern int open_cfw_gx8002_audio_frame(uint32_t,const uint32_t *);
const char open_cfw_gx8002_event_hey[] __attribute__((aligned(1)))="wake up hey even\n";
const char open_cfw_gx8002_event_hi[] __attribute__((aligned(1)))="wake up hi even\n";
const char open_cfw_gx8002_event_start[] __attribute__((aligned(1)))="=====    S:%d, first:%d  =====\n";
const char open_cfw_gx8002_event_range[] __attribute__((aligned(1)))="=====   first push_frame S:%d, E:%d  =====\n";
int open_cfw_gx8002_sample_event(APP_EVENT *event)
{
    void *context; uint32_t ignored;
    open_cfw_gx8002_context_lookup(event->ctx_index,&context,&ignored);
    uint32_t vad=((uint8_t *)context)[12]&7;
    if (vad!=open_cfw_gx8002_event_state.last_vad) {
        open_cfw_gx8002_vad_notify(vad);
        open_cfw_gx8002_event_state.last_vad=((uint8_t *)context)[12]&7;
    }
    if (event->event_id==100) { printf(open_cfw_gx8002_event_hey); open_cfw_gx8002_event_notify(event->event_id); }
    if (event->event_id==101) { printf(open_cfw_gx8002_event_hi); open_cfw_gx8002_event_notify(event->event_id); }
    if (event->event_id==91 && open_cfw_gx8002_event_app[5] && open_cfw_gx8002_event_state.pending) {
        printf(open_cfw_gx8002_event_start,event->ctx_index,1);
        uint32_t address0=0,length0=0,address1=0,length1=0;
        open_cfw_gx8002_mic_buffer(*(const uint32_t **)context,0,event->ctx_index,&address0,&length0);
        open_cfw_gx8002_mic_buffer(*(const uint32_t **)context,1,event->ctx_index,&address1,&length1);
        uint32_t range[2];range[0]=address0-open_cfw_gx8002_event_app[6];range[1]=range[0]+length0-1;
        printf(open_cfw_gx8002_event_range,range[0],range[1]);
        open_cfw_gx8002_audio_frame(open_cfw_gx8002_event_app[1],range);
        open_cfw_gx8002_event_state.pending=0;
    }
    return 0;
}
