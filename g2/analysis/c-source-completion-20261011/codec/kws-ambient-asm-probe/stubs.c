#include <stdint.h>
int32_t gx8002_xip_model_cmd_size_10208bf4(void) { return 16; }
int32_t gx8002_xip_model_weight_size_10208bfc(void) { return 20; }
int32_t gx8002_xip_model_ops_size_10208c04(void) { return 24; }
int32_t gx8002_xip_model_data_size_10208c08(void) { return 32; }
int32_t gx8002_xip_model_tmp_size_10208c10(void) { return 40; }
uint32_t g2_codec_timestamp(void) { static uint32_t tick; return ++tick; }
int32_t gx8002_resident_flash_probe_2475c(uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{ (void)a; (void)b; (void)c; (void)d; return 1; }
int32_t gx8002_resident_flash_dispatch_read_247b8(const volatile uint8_t *a,uint32_t b,uint32_t c,uint32_t d)
{ (void)a; (void)b; (void)c; (void)d; return 0; }
uint32_t gx8002_xip_tws_publish_10206c24(const char *format, ...)
{ (void)format; return 0; }
void gx8002_resident_memcpy_25738(void *destination,const void *source,uint32_t count)
{
    uint8_t *out=destination;
    const uint8_t *in=source;
    for (uint32_t i=0;i<count;i++) out[i]=in[i];
}
