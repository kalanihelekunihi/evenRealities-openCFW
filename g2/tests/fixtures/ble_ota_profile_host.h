#ifndef OPEN_CFW_BLE_OTA_PROFILE_HOST_H
#define OPEN_CFW_BLE_OTA_PROFILE_HOST_H
#include <stdint.h>
struct open_cfw_ota_control;
extern struct open_cfw_ota_control open_cfw_test_ota_control;
#define OPEN_CFW_OTA_CONTROL (&open_cfw_test_ota_control)
#define OPEN_CFW_OTA_WRITE(d,n) open_cfw_test_ota_write((d),(n))
#define OPEN_CFW_OTA_RESET_REQUEST(a,b) open_cfw_test_ota_reset_request((a),(b))
#define OPEN_CFW_OTA_CONNECTION_CLOSE(i) open_cfw_test_ota_connection_close(i)
#define OPEN_CFW_OTA_DELAY(c,a,d) open_cfw_test_ota_delay((c),(a),(d))
#define OPEN_CFW_OTA_CONNECTION_ROLE(i) open_cfw_test_ota_connection_role(i)
#define OPEN_CFW_OTA_CANCEL_EXPORT() open_cfw_test_ota_cancel_export()
#define OPEN_CFW_OTA_SERVICE_INIT() open_cfw_test_ota_service_init()
#define OPEN_CFW_OTA_CONNECTION_STATE() open_cfw_test_ota_connection_state()
#define OPEN_CFW_OTA_WAIT_TX_READY() open_cfw_test_ota_wait_tx_ready()
#define OPEN_CFW_OTA_TX_COMPLETE_NOTIFY() open_cfw_test_ota_tx_complete_notify()
#define OPEN_CFW_OTA_MESSAGE_ALLOC(n) open_cfw_test_ota_message_alloc(n)
#define OPEN_CFW_OTA_MESSAGE_SEND(h,m) open_cfw_test_ota_message_send((h),(m))
#define OPEN_CFW_OTA_NOTIFY(...) open_cfw_test_ota_notify(__VA_ARGS__)
#define OPEN_CFW_OTA_DISCONNECT_CALLBACK open_cfw_test_ota_disconnect_callback
uint8_t open_cfw_test_ota_write(const uint8_t*,uint16_t);
void open_cfw_test_ota_reset_request(uint32_t,uint32_t);
void open_cfw_test_ota_connection_close(uint8_t);
void open_cfw_test_ota_delay(void(*)(void*),void*,uint32_t);
uint8_t open_cfw_test_ota_connection_role(uint8_t);
void open_cfw_test_ota_cancel_export(void);
void open_cfw_test_ota_service_init(void);
uint8_t open_cfw_test_ota_connection_state(void);
void open_cfw_test_ota_wait_tx_ready(void);
void open_cfw_test_ota_tx_complete_notify(void);
void *open_cfw_test_ota_message_alloc(uint16_t);
void open_cfw_test_ota_message_send(uint8_t,void*);
void open_cfw_test_ota_notify(uint8_t,uint16_t,uint16_t,const uint8_t*);
void open_cfw_test_ota_disconnect_callback(void*);
void open_cfw_test_ota_reset(void);
void open_cfw_test_ota_set(uint32_t,uint32_t);
uint32_t open_cfw_test_ota_word(uint32_t);
#endif
