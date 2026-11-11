/* Native ST25 identity adapter 0x77c50 and board probe 0x503b4.
 * Return the byte written by ReadID even when registration/ReadID reports an
 * error. Repeated logging-mode queries and byte reloads are intentional. */
#include <stdint.h>
#include "stock_bus_bindings.h"
#include "st25dvxxkc.h"
extern ST25DVxxKC_Object_t r1_st25_device;
/* Exported by the pinned provider C file; omitted from its public header. */
extern int32_t ST25DVxxKC_ReadID(const ST25DVxxKC_Object_t *,uint8_t *);
extern void nrf_delay_ms(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
const char r1_nfc_identity_ring[] __attribute__((section(".r1.nfc.id.ring")))="[RING]nfctag_id = 0x%x ";
const char r1_nfc_identity_sdk[] __attribute__((section(".r1.nfc.id.sdk")))="nfctag_id = 0x%x ";
const char r1_nfc_probe_ring[] __attribute__((section(".r1.nfc.probe.ring")))="[RING]bc_nfc_st25dv_device_chip_id:%02x \r";
const char r1_nfc_probe_sdk[] __attribute__((section(".r1.nfc.probe.sdk")))="bc_nfc_st25dv_device_chip_id:%02x \r";
__attribute__((noinline)) uint32_t r1_st25dvxxkc_identity_log_adapter(void)
{
    /* ReadID owns one byte. Upper scratch bytes and caller-clobbered R3
     * are not outputs of this C interface. Keep word-sized backing storage. */
    volatile uint32_t word=0;
    (void)r1_st25dvxxkc_register_provider();
    (void)ST25DVxxKC_ReadID(&r1_st25_device,(uint8_t *)(uintptr_t)&word);
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x0c400000,r1_nfc_identity_ring,r1_nfc_identity_ring,(uint32_t)((volatile uint8_t *)&word)[0]);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_nfc_identity_sdk,((volatile uint8_t *)&word)[0]);
    return ((volatile uint8_t *)&word)[0];
}
__attribute__((noinline)) uint32_t r1_nfc_chip_id_probe(void)
{
    r1_i2c5_nfc_resource_acquire();
    nrf_delay_ms(50);
    uint32_t id=r1_st25dvxxkc_identity_log_adapter();
    r1_i2c5_nfc_resource_release();
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x0c400000,r1_nfc_probe_ring,r1_nfc_probe_ring,id);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,r1_nfc_probe_sdk,id);
    return id;
}
