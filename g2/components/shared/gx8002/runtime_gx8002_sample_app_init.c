/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct sample_state { uint32_t limit; void *handle; uint32_t lock,countdown,initialized; };
extern struct sample_state open_cfw_gx8002_sample_state;
extern int printf(const char *,...);
extern void open_cfw_gx8002_sample_setup(void);
extern int open_cfw_gx8002_power_lock_create(uint32_t *);
const char open_cfw_gx8002_sample_init_name[] __attribute__((aligned(1)))="SampleAppInit";
const char open_cfw_gx8002_sample_init_message[] __attribute__((aligned(1)))="[YW_APP][%s]%d\n";
int open_cfw_gx8002_sample_app_init(void)
{
    if (!open_cfw_gx8002_sample_state.initialized) {
        open_cfw_gx8002_sample_state.initialized=1;
        printf(open_cfw_gx8002_sample_init_message,open_cfw_gx8002_sample_init_name,349);
        open_cfw_gx8002_sample_setup();
        open_cfw_gx8002_power_lock_create(&open_cfw_gx8002_sample_state.lock);
    }
    return 0;
}
