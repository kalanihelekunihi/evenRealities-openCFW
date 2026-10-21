/* Native image-B main 0x10015cfc..0x10015d23. The six downstream product
 * routines are genuine entry-reachable code contracts pending source audit. */
#include <stdint.h>

extern void gx8002_image_b_main_initial_1000a8ec(void);
extern uint32_t gx8002_image_b_main_mode_1000b748(uint32_t);
extern void gx8002_image_b_main_services_1000bdfc(void);
extern uint32_t gx8002_image_b_main_poll_1000b7a0(void);
extern void gx8002_image_b_main_finish_1000aacc(void);
extern void gx8002_image_b_main_continue_1000be5c(void);

int32_t gx8002_image_b_main_10015cfc(void)
{
    gx8002_image_b_main_initial_1000a8ec();
    gx8002_image_b_main_mode_1000b748(5u);
    gx8002_image_b_main_services_1000bdfc();
    for (;;) {
        uint32_t status = gx8002_image_b_main_poll_1000b7a0();
        if (status == 0) {
            gx8002_image_b_main_finish_1000aacc();
            return status;
        }
        gx8002_image_b_main_continue_1000be5c();
    }
}
