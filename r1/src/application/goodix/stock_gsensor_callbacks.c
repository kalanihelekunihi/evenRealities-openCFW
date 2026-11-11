/* Stock 815cc: reject any null word without changing the callback table. */
#include "stock_gsensor_callbacks.h"
_Static_assert(sizeof(struct r1_goodix_gsensor_callbacks) == 12,
               "native callback table extent");
_Static_assert(__builtin_offsetof(struct r1_goodix_gsensor_callbacks, sample) == 8,
               "native sample callback offset");
volatile struct r1_goodix_gsensor_callbacks r1_goodix_gsensor_callbacks
    __attribute__((section(".bss.r1.goodix.gsensor.callbacks"), aligned(4)));
uint32_t r1_goodix_gsensor_register(uintptr_t start, uintptr_t stop,
                                   uintptr_t sample)
{
    if (start == 0 || stop == 0 || sample == 0)
        return 0;
    r1_goodix_gsensor_callbacks.start = start;
    r1_goodix_gsensor_callbacks.stop = stop;
    r1_goodix_gsensor_callbacks.sample = sample;
    return 1;
}

/* Native 6f9d4: dispatch the live stop slot without a scratch frame. */
void r1_goodix_gsensor_stop(void)
{
    uintptr_t stop = r1_goodix_gsensor_callbacks.stop;
    if (stop != 0) {
        __attribute__((musttail)) return ((void (*)(void))stop)();
    }
}

extern void r1_gsensor_sample_sink_nop(uint32_t, int32_t, int32_t, int32_t);
/* Native 6f920: R1 retains the incoming count pointer across the optional
 * board call. Volatile reads preserve the live count and Z/Y/X access order. */
void r1_goodix_gsensor_sample(int16_t *samples, uint16_t *count)
{
    uintptr_t sample = r1_goodix_gsensor_callbacks.sample;
    if (sample != 0)
        ((void (*)(int16_t *, uint16_t *))sample)(samples, count);
    uint32_t index = 0;
    uint16_t live;
    while ((live = *(volatile uint16_t *)count) > index) {
        volatile int16_t *axis = samples + index * 3;
        int32_t z = axis[2];
        int32_t y = axis[1];
        int32_t x = axis[0];
        r1_gsensor_sample_sink_nop(0, x, y, z);
        ++index;
    }
    if (live > 100) {
        for (;;) {}
    }
}

#include <stddef.h>
extern void *memset(void *,int,size_t);
/* Native 6f964: 184 scratch bytes, of which only the first 180 are cleared.
 * The format/print pointers and board start slot are sampled in native order. */
typedef int (*r1_goodix_format_fn)(char *,size_t,const char *,...);
typedef int (*r1_goodix_print_fn)(const char *,...);
extern r1_goodix_format_fn g_pSnprintfUserIn;
extern r1_goodix_print_fn g_pPrintfUserIn;
extern void GH3X2X_TimestampSyncAccInit(void);
static const char message[]="[LOG_D] hal_gsensor_start_cache_data\r\n";
void r1_goodix_gsensor_cache_commit(void)
{
 char buffer[184];
 r1_goodix_format_fn format=*(r1_goodix_format_fn volatile *)&g_pSnprintfUserIn;
 if(format){(void)format(memset(buffer,0,180),180,message);}
 r1_goodix_print_fn print=*(r1_goodix_print_fn volatile *)&g_pPrintfUserIn;
 if(print)(void)print(message);
 GH3X2X_TimestampSyncAccInit();
 uintptr_t start=r1_goodix_gsensor_callbacks.start;
 if(start){__attribute__((musttail)) return ((void (*)(void))start)();}
}

extern __typeof__(r1_goodix_gsensor_cache_commit) hal_gsensor_start_cache_data
 __attribute__((alias("r1_goodix_gsensor_cache_commit")));
extern __typeof__(r1_goodix_gsensor_stop) hal_gsensor_stop_cache_data
 __attribute__((alias("r1_goodix_gsensor_stop")));
