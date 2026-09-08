/* SPDX-License-Identifier: MIT */
/* Recovered GRUS SNPU hardware shim. The authenticated stock init and exit
 * implementations really are empty returns; these are not fallback stubs. */
typedef int (*open_cfw_snpu_irq_handler)(int irq, void *data);
extern void open_cfw_gx8002_request_irq(int irq,
                                     open_cfw_snpu_irq_handler handler,
                                     void *data);
/* gx_snpu_init passes the register base; this hardware hook ignores it. */
void open_cfw_gx8002_snpu_device_init(void *register_base)
{
    (void)register_base;
}
void open_cfw_gx8002_snpu_device_exit(void) {}
void open_cfw_gx8002_snpu_request_irq(open_cfw_snpu_irq_handler handler,
                                    void *data)
{
    open_cfw_gx8002_request_irq(12, handler, data);
}
