#include <stdint.h>
#include <stddef.h>
extern volatile uint32_t r1_gomore_native_context;
extern uint32_t r1_gomore_ppg_resample_native(uint32_t,volatile uint32_t *,uint32_t,uint32_t,volatile uint32_t *);
extern uint32_t r1_gomore_acc_resample_native(uint32_t,volatile uint32_t *,uint32_t,volatile uint32_t *);
extern uint32_t r1_gomore_algorithm_output_native(uint32_t,uint32_t);
struct __attribute__((packed,may_alias)) host_word {uint32_t value;};
struct __attribute__((packed,may_alias)) host_half {uint16_t value;};
static uint32_t word(uint32_t address)
{ return ((const volatile struct host_word *)(uintptr_t)address)->value; }
static void put_word(uint32_t address,uint32_t value)
{ ((volatile struct host_word *)(uintptr_t)address)->value=value; }
static uint16_t half(uint32_t address)
{ return ((const volatile struct host_half *)(uintptr_t)address)->value; }
static void put_half(uint32_t address,uint16_t value)
{ ((volatile struct host_half *)(uintptr_t)address)->value=value; }
static uint8_t byte(uint32_t address)
{ return *(const volatile uint8_t *)(uintptr_t)address; }
static void put_byte(uint32_t address,uint8_t value)
{ *(volatile uint8_t *)(uintptr_t)address=value; }
static void copy_float(uint32_t source,uint32_t destination)
{ *(volatile float *)(uintptr_t)destination=*(const volatile float *)(uintptr_t)source; }
struct host_input_frame {
    uint32_t acc_sources[3];
    uint8_t acc_outputs[3][100];
    uint32_t raw_source,ppg_source;
    uint8_t ppg_output[100];
};
_Static_assert(sizeof(struct host_input_frame)==420,"native host scratch view");
_Static_assert(offsetof(struct host_input_frame,acc_outputs)==12,"axis scratch view");
_Static_assert(offsetof(struct host_input_frame,ppg_source)==316,"PPG source view");
_Static_assert(offsetof(struct host_input_frame,ppg_output)==320,"PPG scratch view");
uint32_t r1_gomore_host_input_update_native(volatile void *packet,uint32_t index)
{
    _Alignas(8) volatile struct host_input_frame frame;
    uint32_t data=(uint32_t)(uintptr_t)packet;
    uint32_t context=r1_gomore_native_context;
    put_word(context+400u,index);
    put_half(context+396u,half(data+4u));
    frame.ppg_source=word(data+24u);
    put_word(context+368u,(uint32_t)(uintptr_t)frame.ppg_output);
    uint32_t count=byte(data+28u),channels=byte(data+29u);
    (void)r1_gomore_ppg_resample_native(context,&frame.ppg_source,channels,count,
        (volatile uint32_t *)(uintptr_t)(context+368u));
    if (byte(data+48u)) put_byte(r1_gomore_native_context+372u,1);
    context=r1_gomore_native_context;
    put_byte(context+373u,byte(data+48u));
    frame.raw_source=word(data+24u);
    put_half(context+380u,byte(data+28u));
    uint32_t ready=byte(data+29u);
    if (ready>1) ready=1;
    put_byte(context+382u,(uint8_t)ready);
    uint32_t missing=1;
    if (byte(data+29u) && byte(data+28u)) missing=0;
    put_byte(context+383u,(uint8_t)missing);
    put_word(context+376u,frame.raw_source);
    frame.acc_sources[0]=word(data+8u);
    frame.acc_sources[1]=word(data+12u);
    frame.acc_sources[2]=word(data+16u);
    for (uint32_t i=0;i<3;i++)
        put_word(context+456u+i*4u,(uint32_t)(uintptr_t)frame.acc_outputs[i]);
    uint32_t acc_count=byte(data+20u);
    (void)r1_gomore_acc_resample_native(context,frame.acc_sources,acc_count,
        (volatile uint32_t *)(uintptr_t)(context+456u));
    context=r1_gomore_native_context;
    copy_float(data+40u,context+364u);
    copy_float(data+44u,context+336u);
    if (word(context+0x39d4u)==2) {
        put_byte(context+757u,byte(data+49u));
        put_byte(context+758u,byte(data+50u));
    }
    uint32_t last=word(word(context+0x39dcu)+4u);
    (void)r1_gomore_algorithm_output_native(context+320u,index-last);
    return 0;
}
