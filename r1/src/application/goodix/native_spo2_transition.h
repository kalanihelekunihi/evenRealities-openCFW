#ifndef R1_NATIVE_SPO2_TRANSITION_H
#define R1_NATIVE_SPO2_TRANSITION_H
void r1_goodix_native_spo2_channel_transition(void *state,const void *summary,const void *filter);
void r1_goodix_spo2_transition(void *state_owner,void *summary,const void *descriptor,void *filter_owner);
#endif
