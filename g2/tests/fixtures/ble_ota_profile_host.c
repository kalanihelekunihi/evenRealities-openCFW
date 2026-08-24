#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
struct open_cfw_ota_control { uint8_t connection_id,handler_id,notifications_enabled,connection_ready; };
struct open_cfw_ota_message { uint16_t parameter;uint8_t event,status;const uint8_t *data;uint16_t length,reserved; };
struct open_cfw_ota_control open_cfw_test_ota_control;
static uint32_t w[32];static struct open_cfw_ota_message msg;
void open_cfw_test_ota_reset(void){uint32_t i;for(i=0;i<32;i++)w[i]=0;open_cfw_test_ota_control=(struct open_cfw_ota_control){0};msg=(struct open_cfw_ota_message){0};}
void open_cfw_test_ota_set(uint32_t i,uint32_t v){if(i<4)((uint8_t*)&open_cfw_test_ota_control)[i]=(uint8_t)v;else if(i==4)w[30]=v;else if(i==5)w[31]=v;}
uint32_t open_cfw_test_ota_word(uint32_t i){return i<4?((uint8_t*)&open_cfw_test_ota_control)[i]:w[i-4];}
uint8_t open_cfw_test_ota_write(const uint8_t*d,uint16_t n){w[0]++;w[1]=n;w[2]=d?d[0]:0;return (uint8_t)w[31];}
void open_cfw_test_ota_reset_request(uint32_t a,uint32_t b){w[3]++;w[4]=a;w[5]=b;}
void open_cfw_test_ota_connection_close(uint8_t i){w[6]++;w[7]=i;}
void open_cfw_test_ota_delay(void(*c)(void*),void*a,uint32_t d){w[8]++;w[9]=(uint32_t)(uintptr_t)c;w[10]=(uint32_t)(uintptr_t)a;w[11]=d;}
uint8_t open_cfw_test_ota_connection_role(uint8_t i){w[12]++;w[13]=i;return (uint8_t)w[30];}
void open_cfw_test_ota_cancel_export(void){w[14]++;}
void open_cfw_test_ota_service_init(void){w[15]++;}
uint8_t open_cfw_test_ota_connection_state(void){w[16]++;return 1;}
void open_cfw_test_ota_wait_tx_ready(void){w[17]++;}
void open_cfw_test_ota_tx_complete_notify(void){w[18]++;}
void *open_cfw_test_ota_message_alloc(uint16_t n){w[19]++;w[20]=n;return w[31]?NULL:&msg;}
void open_cfw_test_ota_message_send(uint8_t h,void*m){struct open_cfw_ota_message*x=m;w[21]++;w[22]=h;w[23]=x->parameter;w[24]=x->event;w[25]=(uint32_t)(uintptr_t)x->data;w[26]=x->length;}
void open_cfw_test_ota_notify(uint8_t i,uint16_t h,uint16_t n,const uint8_t*d){w[27]++;w[28]=i;w[29]=h;w[30]=n;w[31]=d?d[0]:0;}
void open_cfw_test_ota_disconnect_callback(void*a){(void)a;}
