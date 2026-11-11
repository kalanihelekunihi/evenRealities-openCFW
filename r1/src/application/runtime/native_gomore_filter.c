/* Stock IIR state updates: live order, ordered history copies, non-fused FP. */
#include <stdint.h>
static __attribute__((noinline,noclone)) float multiply(float a,float b){return a*b;}
static __attribute__((noinline,noclone)) float multiply_add(float acc,float a,float b){return acc+a*b;}
static __attribute__((noinline,noclone)) float multiply_sub(float acc,float a,float b){return acc-a*b;}
struct __attribute__((packed,may_alias)) filter_word {uint32_t value;};
static uint32_t word(uint32_t a){return ((volatile struct filter_word *)(uintptr_t)a)->value;}
static void put_word(uint32_t a,uint32_t v){((volatile struct filter_word *)(uintptr_t)a)->value=v;}
static float sample(uint32_t a){return *(volatile float *)(uintptr_t)a;}
static void put_sample(uint32_t a,float v){*(volatile float *)(uintptr_t)a=v;}
uint32_t r1_gomore_filter_native(uint32_t state,uint32_t values,uint32_t count)
{
    for (uint32_t i=0;(int32_t)i<(int32_t)count;i++) {
        uint32_t at=values+i*4u;
        float a=sample(state+28u),b=sample(at);
        float output=multiply(a,b);
        uint32_t order=word(state);
        for (uint32_t j=1;(int32_t)j<=(int32_t)order;j++) {
            float history=sample(state+48u+(j-1u)*4u);
            float coefficient=sample(state+28u+j*4u);
            output=multiply_add(output,history,coefficient);
            history=sample(state+64u+(j-1u)*4u);
            coefficient=sample(state+8u+j*4u);
            output=multiply_sub(output,history,coefficient);
        }
        for (uint32_t j=order-1u;(int32_t)j>0;j--) {
            float previous=sample(state+48u+(j-1u)*4u);
            put_sample(state+48u+j*4u,previous);
            previous=sample(state+64u+(j-1u)*4u);
            put_sample(state+64u+j*4u,previous);
        }
        b=sample(at);
        put_sample(state+48u,b);
        put_sample(state+64u,output);
        put_sample(at,output);
    }
    put_word(state+4u,1);
    return state;
}
