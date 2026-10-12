/* Native image-B 0x100089e8..0x100089f7 reads mutable gsensor workstate
 * twice: once for logging, then again for its return value. The RAM word
 * at 0x20016f60 is a real product state/linker contract.
 * Stock SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>
extern volatile uint32_t gx8002_image_b_gsensor_workstate_20016f60;
extern int gx8002_image_b_heap_log_10009934(const char *, ...);

uint32_t gx8002_image_b_gsensor_workstate_100089e8(void)
{
    uint32_t observed = gx8002_image_b_gsensor_workstate_20016f60;
    (void)gx8002_image_b_heap_log_10009934(
        "gsensor_workstate =%d\n", observed);
    return gx8002_image_b_gsensor_workstate_20016f60;
}
