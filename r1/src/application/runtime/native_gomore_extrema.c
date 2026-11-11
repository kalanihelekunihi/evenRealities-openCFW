#include <stdint.h>
static __attribute__((noinline,noclone)) float add(float a,float b){return a+b;}
static __attribute__((noinline,noclone)) float sub(float a,float b){return a-b;}
static __attribute__((noinline,noclone)) float divide(float a,float b){return a/b;}
static __attribute__((noinline,noclone)) float convert(uint32_t value){return (float)value;}
static __attribute__((noinline,noclone)) uint32_t greater(float a,float b){return a>b;}
static __attribute__((noinline,noclone)) uint32_t less(float a,float b){return a<b;}
static float sample(uint32_t at){return *(volatile float *)(uintptr_t)at;}
static void put(uint32_t at,uint32_t value){*(volatile uint8_t *)(uintptr_t)at=(uint8_t)value;}
uint32_t r1_gomore_extrema_native(uint32_t values,uint32_t count,uint32_t long_window,uint32_t short_window,volatile uint32_t maxima,volatile uint32_t minima,volatile uint32_t maxima_count,volatile uint32_t minima_count)
{
    put(minima_count,0);put(maxima_count,0);
    uint32_t maximum_count=0,minimum_count=0,index=0,previous=0;
    uint32_t long_half=long_window>>1,short_half=short_window>>1,last=count-1u;
    float long_sum=0.0f,short_sum=0.0f,best=0.0f;
    for(uint32_t i=0;(int32_t)i<(int32_t)count;i++) {
        if(!i) {
            for(uint32_t offset=0u-long_half;(int32_t)offset<(int32_t)(long_window-long_half);offset++) {
                float value=sample(values+((int32_t)offset<0?0u:offset)*4u);
                long_sum=add(value,long_sum);
            }
            for(uint32_t offset=0u-short_half;(int32_t)offset<(int32_t)(short_window-short_half);offset++) {
                float value=sample(values+((int32_t)offset<0?0u:offset)*4u);
                short_sum=add(value,short_sum);
            }
        } else {
            uint32_t outgoing=i-long_half-1u;
            float value=sample(values+((int32_t)outgoing<0?0u:outgoing)*4u);
            long_sum=sub(long_sum,value);
            uint32_t incoming=long_window-long_half+i-1u;
            value=sample(values+((int32_t)incoming>(int32_t)last?last:incoming)*4u);
            long_sum=add(value,long_sum);
            outgoing=i-short_half-1u;
            value=sample(values+((int32_t)outgoing<0?0u:outgoing)*4u);
            short_sum=sub(short_sum,value);
            incoming=short_window-short_half+i-1u;
            value=sample(values+((int32_t)incoming>(int32_t)last?last:incoming)*4u);
            short_sum=add(value,short_sum);
        }
        float long_mean=divide(long_sum,convert(long_window));
        float short_mean=divide(short_sum,convert(short_window));
        uint32_t above=greater(short_mean,long_mean);
        if(!i) {best=sample(values);index=0;}
        else if(previous!=above) {
            if(previous) {
                if(maximum_count>=20u) goto full;
                put(maxima+maximum_count,index);maximum_count=(maximum_count+1u)&255u;
            } else {
                if(minimum_count>=20u) goto full;
                put(minima+minimum_count,index);minimum_count=(minimum_count+1u)&255u;
            }
            best=sample(values+i*4u);index=i&255u;
        } else {
            float value=sample(values+i*4u);
            if(above?greater(value,best):less(value,best)) {best=value;index=i&255u;}
        }
        previous=above;
    }
    put(maxima_count,maximum_count);put(minima_count,minimum_count);return 0;
full:
    put(minima_count,0);put(maxima_count,0);return 1;
}
