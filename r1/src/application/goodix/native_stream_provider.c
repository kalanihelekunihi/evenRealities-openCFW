#include <stdint.h>
#include <stddef.h>
#include "native_stream_callbacks.h"
typedef struct __attribute__((packed,may_alias)) {uint32_t value;} stream_word;
typedef struct __attribute__((packed,may_alias)) {uint16_t value;} stream_half;
static uint32_t word(const volatile uint8_t *p){return ((const volatile stream_word *)p)->value;}
static void put(volatile uint8_t *p,uint32_t v){((volatile stream_word *)p)->value=v;}
static uint32_t half(const volatile uint8_t *p){return ((const volatile stream_half *)p)->value;}
static void put_half(volatile uint8_t *p,uint32_t v){((volatile stream_half *)p)->value=(uint16_t)v;}
extern void __aeabi_memclr(void *,size_t);
extern void *r1_native_memory_move(void *,const void *,size_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern uint32_t r1_goodix_reference_counted_acquire(uint32_t),r1_goodix_reference_counted_release(uint32_t);
extern uint32_t r1_stream_tick_now(void),r1_goodix_initialize_probe(void);
extern void r1_goodix_i2c_open(void),r1_goodix_i2c_close(void),Gh3x2xDemoInterruptProcess(void);
extern void *r1_stream_object_create(const char *,uint32_t,const void *,uint32_t);
extern uint32_t r1_stream_object_flag_set(volatile uint8_t *,uint32_t);
volatile uint32_t r1_goodix_stream_last_poll
 __attribute__((section(".r1.goodix.stream.last_poll"),aligned(4)));
const char r1_goodix_stream_open_ring[]="[RING]ppg open type:%d";
const char r1_goodix_stream_open_sdk[]="ppg open type:%d";
/* Stock 0x8165c truncates only after testing the full argument for zero. */
uint32_t r1_goodix_open_mode_plan_build(uint32_t context)
{
 if (!context) return 0;
 uint32_t mode=(uint8_t)context;
 if (mode<=4) {
  if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x0c400000,r1_goodix_stream_open_ring,r1_goodix_stream_open_ring,mode);
  if (r1_structured_log_mode_get()&2u)
   nrf_log_frontend_std_1(0x001c0003,r1_goodix_stream_open_sdk,mode);
 }
 switch(mode) {
 case 1:put(r1_goodix_stream_cache,0);put(r1_goodix_stream_cache+4,0);put(r1_goodix_stream_cache+8,0);put(r1_goodix_stream_cache+12,0);break;
 case 2:__aeabi_memclr((void *)(uintptr_t)(r1_goodix_stream_cache+40),24);break;
 case 3:put_half(r1_goodix_stream_cache+188,0);break;
 case 4:__aeabi_memclr((void *)(uintptr_t)(r1_goodix_stream_cache+16),24);break;
 case 5:__aeabi_memclr((void *)(uintptr_t)(r1_goodix_stream_cache+64),124);break;
 case 7:__aeabi_memclr((void *)(uintptr_t)(r1_goodix_stream_cache+216),24);break;
 case 8:put(r1_goodix_stream_cache+192,0);put(r1_goodix_stream_cache+196,0);put(r1_goodix_stream_cache+200,0);break;
 case 9:put(r1_goodix_stream_cache+204,0);put(r1_goodix_stream_cache+208,0);put(r1_goodix_stream_cache+212,0);break;
 default:break;
 }
 return r1_goodix_reference_counted_acquire(mode);
}
uint32_t r1_goodix_stream_close(uint32_t context)
{
 if (!context) return 0;
 return r1_goodix_reference_counted_release((uint8_t)context);
}
/* Stock 0x81744 ignores length. Preserve its fixed output formats and all
 * interleaved cache/output accesses, including overlapping destinations. */
uint32_t r1_goodix_diagnostic_select(uint8_t *destination,uint32_t length __attribute__((unused)),uint32_t context)
{
 volatile uint8_t *out=destination;
 uint32_t mode=(uint8_t)context;
 if (!out) return 0;
 uint32_t now=r1_stream_tick_now(),previous=r1_goodix_stream_last_poll;
 if (now>=previous+500u || previous==0) {
  __aeabi_memclr((void *)(uintptr_t)(r1_goodix_stream_cache+64),124);
  __aeabi_memclr((void *)(uintptr_t)(r1_goodix_stream_cache+216),24);
  r1_goodix_i2c_open();Gh3x2xDemoInterruptProcess();r1_goodix_i2c_close();
  r1_goodix_stream_last_poll=now;
 }
 volatile uint8_t *cache=r1_goodix_stream_cache;
 uint32_t value;
 switch(mode) {
 case 1:
  value=word(cache);if(value-41u>=179u)return 0;
  out[0]=(uint8_t)value;out[1]=cache[4];out[2]=cache[8];out[3]=cache[12];return 4;
 case 2:
  value=word(cache+40);if(!value)return 0;
  out[0]=(uint8_t)value;out[1]=cache[44];out[2]=cache[48];out[3]=cache[52];out[4]=cache[56];out[5]=cache[60];return 6;
 case 3:
  if(cache[188]!=1)return 0;
  cache[188]=0;put_half(out,half(cache+188));return 2;
 case 4:
  value=word(cache+16);if(!value)return 0;
  put_half(out,value);put_half(out+2,half(cache+20));put_half(out+4,half(cache+24));put_half(out+6,half(cache+28));
  out[8]=cache[32];out[9]=cache[36];return 10;
 case 5:(void)r1_native_memory_move((void *)(uintptr_t)out,(const void *)(uintptr_t)(cache+64),124);return 124;
 case 7:(void)r1_native_memory_move((void *)(uintptr_t)out,(const void *)(uintptr_t)(cache+216),24);return 24;
 case 8:
  value=word(cache+192);put(out,value);value=word(cache+196);put(out+4,value);value=word(cache+200);put(out+8,value);return 12;
 case 9:
  value=word(cache+204);put(out,value);value=word(cache+208);put(out+4,value);value=word(cache+212);put(out+8,value);return 12;
 default:return 0;
 }
}
struct r1_goodix_stream_ops {
 uint32_t (*open)(uint32_t),(*close)(uint32_t);
 uint32_t (*read)(uint8_t *,uint32_t,uint32_t);
};
_Static_assert(sizeof(struct r1_goodix_stream_ops)==12,"native Goodix stream operation table");
const struct r1_goodix_stream_ops r1_goodix_stream_operations
 __attribute__((section(".r1.goodix.stream.operations"),aligned(4)))={r1_goodix_open_mode_plan_build,r1_goodix_stream_close,r1_goodix_diagnostic_select};
/* Native 0x89eec installs callbacks before creating and enabling each stream. */
uint32_t r1_native_stream_register(void)
{
 (void)r1_goodix_initialize_probe();__aeabi_memclr((void *)(uintptr_t)(r1_goodix_stream_cache),240);
 (void)r1_stream_cfg_set_00((uint32_t)(uintptr_t)r1_goodix_stream_hr);
 (void)r1_stream_cfg_set_08((uint32_t)(uintptr_t)r1_goodix_stream_spo2);
 (void)r1_stream_cfg_set_04((uint32_t)(uintptr_t)r1_goodix_raw_hr_append);
 (void)r1_stream_cfg_set_0c((uint32_t)(uintptr_t)r1_goodix_wear_living_object_update);
 (void)r1_stream_cfg_set_10((uint32_t)(uintptr_t)r1_goodix_stream_gray);
 (void)r1_stream_cfg_set_14((uint32_t)(uintptr_t)r1_goodix_stream_gain);
 (void)r1_stream_cfg_set_1c((uint32_t)(uintptr_t)r1_goodix_stream_aging);
 (void)r1_stream_cfg_set_18((uint32_t)(uintptr_t)r1_goodix_adt_append);
 static const struct {const char *name;uint32_t bytes,context;} streams[]={
  {"hr",4,1},{"spo2",6,2},{"raw_hr",124,5},{"wear",2,3},
  {"gray",12,8},{"aging",12,9},{"hrv",10,4},{"adt",24,7}};
 uint32_t result=0;
 for(uint32_t i=0;i<8;++i){
  void *object=r1_stream_object_create(streams[i].name,streams[i].bytes,&r1_goodix_stream_operations,streams[i].context);
  result=r1_stream_object_flag_set(object,1);
 }
 return result;
}
