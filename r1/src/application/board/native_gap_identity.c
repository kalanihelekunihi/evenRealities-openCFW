/* Stock GAP identity 0x66c4c and checked preferred parameters 0x4e48c.
 * Pinned S140 declarations own the controller gateway. */
#include <stdint.h>
#include <string.h>
#include "ble_gap.h"
#include "ble_conn_state.h"
#include "native_ble_identity.h"
extern void r1_adc_error(uint32_t);
extern uint32_t r1_advertising_configuration_byte_get(void);
extern int r1_native_sprintf(char *,const char *,...);
volatile uint8_t r1_connection_parameter_profile
 __attribute__((section(".r1.ble.connection_parameter_profile"),aligned(1)))=1;
volatile uint8_t r1_ble_controller_address[7]
 __attribute__((section(".r1.ble.controller_address"),aligned(1)))={0};
volatile uint8_t r1_ble_phone_peer_address[7]
 __attribute__((section(".r1.ble.phone_peer_address"),aligned(1)))={0};
volatile uint8_t r1_ble_glasses_peer_address[7]
 __attribute__((section(".r1.ble.glasses_peer_address"),aligned(1)))={0};
char r1_ble_device_name[32]
 __attribute__((section(".r1.ble.device_name"),aligned(1)))="EVEN R1";
/* Stock 0x4cb9c: address of the mutable advertised device name. */
const char *r1_identity_data_ptr_get(void) { return r1_ble_device_name; }
const ble_gap_conn_params_t r1_gap_preferred_parameter_profiles[2]={
    {12,24,4,600},{12,24,4,600}
};
uint32_t r1_gap_ppcp_set_checked(void)
{
    const ble_gap_conn_params_t *parameters=&r1_gap_preferred_parameter_profiles[
        r1_connection_parameter_profile!=0];
    uint32_t status=sd_ble_gap_ppcp_set(parameters);
    if (status) r1_adc_error(status);
    return status;
}
void r1_nordic_gap_identity_configuration(void)
{
    ble_gap_conn_sec_mode_t security={0};
    BLE_GAP_CONN_SEC_MODE_SET_OPEN(&security);
    /* Native leaves failed-query output in private stack bytes. Define a C
     * fallback for unwritten bytes while preserving error continuation. */
    ble_gap_addr_t address={0};
    uint32_t status=sd_ble_gap_addr_get(&address);
    if (status) r1_adc_error(status);
    for (uint32_t i=0;i<7;i++) r1_ble_phone_peer_address[i]=0;
    for (uint32_t i=0;i<7;i++) r1_ble_glasses_peer_address[i]=0;
    const uint8_t *bytes=(const uint8_t *)&address;
    for (uint32_t i=0;i<7;i++) r1_ble_controller_address[i]=bytes[i];
    memset(r1_ble_device_name,0,sizeof(r1_ble_device_name));
    uint32_t config=r1_advertising_configuration_byte_get();
    uint32_t low=address.addr[0],middle=address.addr[1],high=address.addr[2];
    (void)r1_native_sprintf(r1_ble_device_name,
        config==0x55 ? "%s_%02X%02X%02X_FAC":"%s_%02X%02X%02X",
        "EVEN R1",high,middle,low);
    uint16_t length=(uint16_t)strlen(r1_ble_device_name);
    status=sd_ble_gap_device_name_set(&security,(const uint8_t *)r1_ble_device_name,length);
    if (status) r1_adc_error(status);
    status=sd_ble_gap_appearance_set(0x240);
    if (status) r1_adc_error(status);
    (void)r1_gap_ppcp_set_checked();
    ble_conn_state_init();
}
