#include <stdint.h>
#include <stddef.h>
/* Packed volatile fields retain native unaligned access widths and order. */
typedef struct __attribute__((packed,may_alias)) { uint32_t value; } wire32;
typedef struct __attribute__((packed,may_alias)) { uint16_t value; } wire16;
_Static_assert(sizeof(wire32)==4 && _Alignof(wire32)==1 && sizeof(wire16)==2 && _Alignof(wire16)==1,"wire access ABI");
extern uint8_t r1_health_storage_hr_prefix[],r1_health_storage_hrv_prefix[],r1_health_storage_spo2_prefix[];
uint32_t r1_hr_latest_packed(void *),r1_hrv_latest_packed(void *),r1_spo2_latest_packed(void *);

__attribute__((noinline,used)) static uint32_t
latest_sample_body(volatile uint8_t *output,volatile uint32_t *frame,uint32_t kind)
{
    if (!output) return 0;
    if (kind==0) {
        ((volatile wire32 *)output)->value=0;
        ((volatile wire32 *)(output+4))->value=0;
    } else if (kind==1) {
        ((volatile wire16 *)output)->value=0;
        ((volatile wire16 *)(output+2))->value=0;
        ((volatile wire32 *)(output+4))->value=0;
    } else {
        output[0]=0;
        ((volatile wire32 *)(output+4))->value=0;
    }
    frame[0]=0;frame[1]=0;
    uint32_t result=kind==0 ? r1_hr_latest_packed((void *)frame) :
        (kind==1 ? r1_hrv_latest_packed((void *)frame) : r1_spo2_latest_packed((void *)frame));
    if (result) {
        const volatile uint8_t *source=(const volatile uint8_t *)frame;
        if (kind==1) {
            ((volatile wire16 *)output)->value=((const volatile wire16 *)source)->value;
            ((volatile wire32 *)(output+4))->value=((const volatile wire32 *)(source+2))->value;
        } else {
            output[0]=source[0];
            ((volatile wire32 *)(output+4))->value=((const volatile wire32 *)(source+1))->value;
        }
    }
    return result;
}

/* Ordinary C owns the initialized provider scratch. Caller-scratch register
 * values and the private frame address are outside the public C interface. */
#define LATEST_ENTRY(name,kind) \
uint32_t name(void *output) \
{ volatile uint32_t frame[2];return latest_sample_body(output,frame,kind); }
LATEST_ENTRY(r1_hr_latest_sample,0)
LATEST_ENTRY(r1_hrv_latest_sample,1)
LATEST_ENTRY(r1_spo2_latest_sample,2)
#undef LATEST_ENTRY
