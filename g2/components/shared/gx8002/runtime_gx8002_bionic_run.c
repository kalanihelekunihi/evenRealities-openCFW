/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct bionic_state { float ctc_offset,bunkws_offset; uint32_t ctc_counter,bunkws_counter; };
extern struct bionic_state open_cfw_gx8002_bionic_state;
struct keyword_list { uint32_t count; void *items; };
extern struct keyword_list *LvpGetKwsParamList(void);
extern int printf(const char *, ...);
const char open_cfw_gx8002_bionic_message[] __attribute__((aligned(1)))="[ST]bunkws threshold_offset: %d\n";
int open_cfw_gx8002_bionic_run(void *context,void *keyword,float score,float threshold,float *window)
{
    (void)keyword; (void)score; (void)threshold; (void)window;
    const uint32_t *header=*(const uint32_t **)context;
    uint32_t duration=header[7]*header[9];
    struct keyword_list *list=LvpGetKwsParamList();
    uint32_t timeout=(list->count*1000000u)>>2;
    uint32_t counter=open_cfw_gx8002_bionic_state.bunkws_counter+1;
    open_cfw_gx8002_bionic_state.bunkws_counter=counter;
    if ((int32_t)(counter*duration)>(int32_t)timeout && open_cfw_gx8002_bionic_state.bunkws_offset<150.f) {
        open_cfw_gx8002_bionic_state.bunkws_counter=0;
        float next=open_cfw_gx8002_bionic_state.bunkws_offset+5.f;
        open_cfw_gx8002_bionic_state.bunkws_offset=next>150.f?150.f:next;
        printf(open_cfw_gx8002_bionic_message,(int)open_cfw_gx8002_bionic_state.bunkws_offset);
    }
    return 0;
}
