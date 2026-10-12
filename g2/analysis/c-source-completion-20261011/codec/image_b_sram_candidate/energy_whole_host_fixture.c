#define _GNU_SOURCE
#include <assert.h>
#include <stdarg.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
static int logs;
static uint32_t low_word,high_word;
int gx8002_image_b_heap_log_10009934(const char *format, ...) {
    assert(strcmp(format,"[error]:%d, %d,\n")==0);
    va_list ap; va_start(ap,format);
    low_word=va_arg(ap,uint32_t); high_word=va_arg(ap,uint32_t);
    (void)va_arg(ap,int32_t);
    va_end(ap); ++logs; return 0;
}
extern void gx8002_image_b_energy_whole_experimental(
    const uint32_t *,int16_t *,int32_t,int32_t,volatile uint32_t *);
int main(void) {
    uint32_t *p=mmap((void *)0x19000000,4096,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(p==(void *)0x19000000);
    uint32_t ctx[44]={0};
    ctx[0x18/4]=2; ctx[0xa0/4]=0x19000000;
    ctx[0x98/4]=0x19000020; ctx[0x9c/4]=0x19000040;
    int16_t samples[4]={3,4,0,0}; volatile uint32_t first=1;
    p[0x40/4]=-1; p[0x44/4]=127;
    gx8002_image_b_energy_whole_experimental(ctx,samples,0,0,&first);
    assert(logs==1 && first==1 && p[0]==25);
    /* (float)(-1*116) widens to double -116.0. */
    assert(low_word==0 && high_word==0xc05d0000u);
    assert(p[0x40/4]==25 && p[0x44/4]==0);
    first=0; p[0x40/4]=-1; logs=0; samples[0]=3; samples[1]=4;
    gx8002_image_b_energy_whole_experimental(ctx,samples,0,0,&first);
    assert(first==1 && logs==0 && p[0x40/4]==25);
    return 0;
}
