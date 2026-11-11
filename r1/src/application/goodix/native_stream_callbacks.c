#include <stdint.h>
/* Native Goodix stream result cache @2001a1bc and callback words @20007b8c.
 * Startup ownership is checked against the locked RW/ZI initializer separately. */
volatile uint8_t r1_goodix_stream_cache[240]
 __attribute__((section(".bss.r1.goodix.stream.cache"),aligned(4)));
volatile uint32_t r1_goodix_stream_callbacks[8]
 __attribute__((section(".r1.goodix.stream.callbacks"),aligned(4)));
typedef struct __attribute__((packed,may_alias)) {uint32_t value;} stream_word;
static uint32_t read_word(const volatile void *p)
{return ((const volatile stream_word *)p)->value;}
static void write_word(volatile void *p,uint32_t value)
{((volatile stream_word *)p)->value=value;}
#define SETTER(name,index) uint32_t name(uint32_t callback) { \
 if (!callback) return 0; r1_goodix_stream_callbacks[index]=callback;return 1; }
SETTER(r1_stream_cfg_set_00,0)
SETTER(r1_stream_cfg_set_04,1)
SETTER(r1_stream_cfg_set_08,2)
SETTER(r1_stream_cfg_set_0c,3)
SETTER(r1_stream_cfg_set_10,4)
SETTER(r1_stream_cfg_set_14,5)
SETTER(r1_stream_cfg_set_18,6)
SETTER(r1_stream_cfg_set_1c,7)
uint32_t r1_goodix_adt_append(uint32_t sample)
{
 uint32_t count=r1_goodix_stream_cache[216];
 if(count>=5)return sample;
 write_word(r1_goodix_stream_cache+220+count*4,sample);
 count=r1_goodix_stream_cache[216]+1u;
 r1_goodix_stream_cache[216]=(uint8_t)count;return count;
}
uint32_t r1_goodix_raw_hr_append(uint32_t sample)
{
 uint32_t count=r1_goodix_stream_cache[64];
 if(count>=30)return sample;
 write_word(r1_goodix_stream_cache+68+count*4,sample);
 count=r1_goodix_stream_cache[64]+1u;
 r1_goodix_stream_cache[64]=(uint8_t)count;return count;
}
static uint32_t triple(uint32_t offset,const volatile void *a,const volatile void *b,const volatile void *c)
{
 uint32_t x=read_word(a),y=read_word(b),z=read_word(c);
 write_word(r1_goodix_stream_cache+offset,(x>>31)?0:x);
 write_word(r1_goodix_stream_cache+offset+4,(y>>31)?0:y);
 write_word(r1_goodix_stream_cache+offset+8,(z>>31)?0:z);
 return (uint32_t)(uintptr_t)r1_goodix_stream_cache;
}
uint32_t r1_goodix_stream_gain(const volatile void *a,const volatile void *b,const volatile void *c)
{return triple(204,a,b,c);}
uint32_t r1_goodix_stream_gray(const volatile void *a,const volatile void *b,const volatile void *c)
{return triple(192,a,b,c);}
uint32_t r1_goodix_stream_hr(uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{
 write_word(r1_goodix_stream_cache,a);write_word(r1_goodix_stream_cache+4,b);
 write_word(r1_goodix_stream_cache+8,c);write_word(r1_goodix_stream_cache+12,d);return a;
}
uint32_t r1_goodix_stream_aging(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f)
{
 write_word(r1_goodix_stream_cache+16,a);write_word(r1_goodix_stream_cache+20,b);
 write_word(r1_goodix_stream_cache+24,c);write_word(r1_goodix_stream_cache+28,d);
 write_word(r1_goodix_stream_cache+32,e);write_word(r1_goodix_stream_cache+36,f);return a;
}
uint32_t r1_goodix_stream_spo2(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f)
{
 write_word(r1_goodix_stream_cache+40,a);write_word(r1_goodix_stream_cache+44,b);
 write_word(r1_goodix_stream_cache+48,c);
 uint32_t signed_byte=(d&0x80u)?((d&0xffu)|UINT32_C(0xffffff00)):(d&0xffu);
 write_word(r1_goodix_stream_cache+52,signed_byte);
 write_word(r1_goodix_stream_cache+56,e);write_word(r1_goodix_stream_cache+60,f);return signed_byte;
}
uint32_t r1_goodix_wear_living_object_update(uint32_t value)
{
 r1_goodix_stream_cache[189]=(uint8_t)value;
 r1_goodix_stream_cache[188]=1;return 1;
}
