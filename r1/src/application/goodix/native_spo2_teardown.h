#ifndef R1_GOODIX_NATIVE_SPO2_TEARDOWN_H
#define R1_GOODIX_NATIVE_SPO2_TEARDOWN_H
#include <stdint.h>
extern void *volatile r1_goodix_native_spo2_context;
void r1_goodix_spo2_release_pair(const void *,void *);
void r1_goodix_spo2_release_descriptor_pair(const void *,void *);
void r1_goodix_spo2_release_short_pair(const void *,void *);
void r1_goodix_spo2_release_channel(const void *,void *);
void r1_goodix_spo2_release_session(const void *,void *);
void r1_goodix_spo2_release_aggregate(const void *,void *);
void r1_goodix_spo2_release_owned(const void *,void *);
uint32_t r1_goodix_spo2_release_context_pair(void *);
void r1_goodix_spo2_release_context_record(const void *,void *);
void r1_goodix_spo2_release_channels(const void *,void *);
void r1_goodix_spo2_release_buffer(void *,const void *);
#endif
