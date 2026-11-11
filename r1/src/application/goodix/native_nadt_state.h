#ifndef R1_GOODIX_NATIVE_NADT_STATE_H
#define R1_GOODIX_NATIVE_NADT_STATE_H
#include <stdint.h>
#include <stddef.h>
#include "../../vendor/goodix_primitives/nadt_workspace_view.h"
struct r1_goodix_native_filter {
    const float *numerator;
    const float *denominator;
    float *primary;
    float *secondary;
    uint32_t count;
    float scale;
};
struct r1_goodix_native_nadt_workspace {
    float primary[4];
    float secondary[4];
    int32_t first[100];
    int32_t second[100];
    int16_t small[100];
    int16_t third[200];
    uint32_t history[16];
    struct r1_goodix_native_filter filter;
    uint8_t final[68];
};
struct r1_goodix_native_nadt_state {
    uint8_t flags[28];
    uint16_t counters[6];
    uint32_t values[12];
    void *allocation;
};
extern volatile struct r1_goodix_native_nadt_state r1_goodix_native_nadt_state;
extern struct r1_goodix_native_nadt_workspace r1_goodix_native_nadt_workspace;
goodix_primitives_nadt_stream_workspace_view
r1_goodix_native_nadt_workspace_view(void);
extern const float r1_goodix_native_nadt_denominator[6];
extern const float r1_goodix_native_nadt_numerator[6];
extern volatile uint8_t r1_goodix_native_nadt_configuration[120];
void r1_goodix_native_nadt_reset_fields(void *,uint32_t);
uint32_t r1_goodix_native_nadt_configure(const void *);
extern volatile uint8_t r1_goodix_native_adt_flags[3];
extern volatile uint32_t r1_goodix_native_soft_adt_timeout;
void r1_goodix_native_filter_initialize(volatile struct r1_goodix_native_filter *,
    const float *,const float *,float *,float *,uint32_t,float);
_Static_assert(sizeof(struct r1_goodix_native_filter)==24,"native filter descriptor");
_Static_assert(sizeof(struct r1_goodix_native_nadt_state)==92 && offsetof(struct r1_goodix_native_nadt_state,allocation)==0x58,"native NADT state");
_Static_assert(sizeof(struct r1_goodix_native_nadt_workspace)==1588,"native NADT workspace");
_Static_assert(offsetof(struct r1_goodix_native_nadt_workspace,first)==0x20 && offsetof(struct r1_goodix_native_nadt_workspace,history)==0x598 && offsetof(struct r1_goodix_native_nadt_workspace,filter)==0x5d8 && offsetof(struct r1_goodix_native_nadt_workspace,final)==0x5f0,"native NADT workspace fields");
_Static_assert(offsetof(struct r1_goodix_native_nadt_workspace,second)==0x1b0 &&
               offsetof(struct r1_goodix_native_nadt_workspace,small)==0x340 &&
               offsetof(struct r1_goodix_native_nadt_workspace,third)==0x408,
               "native NADT streaming history banks");
#endif
