/* SPDX-License-Identifier: MIT */
#include "registration.h"
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define FLAGS (*(volatile uint8_t *)(uintptr_t)0x20004543u)
static uint32_t probe(void)
{
    if (FLAGS&2u) return 0x43d574;
    if (FLAGS&1u) return 0x43ce9e;
    if (FLAGS&4u) return 0x43ce9e;
    return 0;
}
static int log_cut(opencfw_pcm_registration_cut_t *cut,uint32_t stage)
{ cut->stage=stage;cut->provider=probe();return cut->provider!=0; }
static void clear12(uintptr_t record)
{
    /* Stock43c0e4 length12 zero fill stores words+4,+8 then+0. This follows
     * word order, not an assertion about architectural multiword atomicity. */
    WORD(record+4)=0;WORD(record+8)=0;WORD(record)=0;
}
void opencfw_pcm_register_prefix(uint32_t owner,uint32_t mode,uint32_t callback,opencfw_pcm_registration_cut_t *cut)
{
    uint32_t selected=(uint8_t)mode;
    cut->provider=0;cut->stage=0;cut->status=0;
    if (selected>=2 || !callback) {cut->status=-1;(void)log_cut(cut,1);return;}
    uintptr_t record=0x20073c20u+12u*selected;
    if (WORD(record+8)) {
        if (log_cut(cut,2)) return;
        clear12(record);
    }
    WORD(record)=owner;
    *(volatile uint8_t *)(record+4)=(uint8_t)mode;
    WORD(record+8)=callback;
    (void)log_cut(cut,3);
}
void opencfw_pcm_unregister_prefix(uint32_t owner,uint32_t mode,opencfw_pcm_registration_cut_t *cut)
{
    uintptr_t record=0x20073c20u+12u*(uint8_t)mode;
    cut->provider=0;cut->stage=0;cut->status=0;
    if (!WORD(record+8)) {(void)log_cut(cut,4);return;}
    if (WORD(record)!=owner) {cut->status=-1;(void)log_cut(cut,5);return;}
    if (log_cut(cut,6)) return;
    clear12(record);
}
