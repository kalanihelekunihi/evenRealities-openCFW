/* SPDX-License-Identifier: MIT */
/* Recovered pin-six application suspend/resume callbacks. */
extern int printf(const char *,...);
extern int open_cfw_gx8002_gpio_disable_trigger(unsigned);
extern int open_cfw_gx8002_padmux_set(unsigned,unsigned);
extern int open_cfw_gx8002_gpio_set_direction(unsigned,unsigned);
extern int open_cfw_gx8002_gpio_enable_trigger(unsigned,unsigned,void (*)(void *),void *);
extern void open_cfw_gx8002_app_gpio_callback(void *);
const char open_cfw_gx8002_app_gpio_message[] __attribute__((aligned(1)))="[YW_APP]%s\n";
int open_cfw_gx8002_app_gpio_suspend(void *private_data)
{
    const char *name = private_data;
    printf(open_cfw_gx8002_app_gpio_message,name);
    open_cfw_gx8002_gpio_disable_trigger(6);
    open_cfw_gx8002_padmux_set(6,0);
    return 0;
}
int open_cfw_gx8002_app_gpio_resume(void *private_data)
{
    const char *name = private_data;
    printf(open_cfw_gx8002_app_gpio_message+8,name);
    open_cfw_gx8002_padmux_set(6,1);
    open_cfw_gx8002_gpio_set_direction(6,0);
    open_cfw_gx8002_gpio_enable_trigger(6,1,open_cfw_gx8002_app_gpio_callback,0);
    return 0;
}
