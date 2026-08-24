#include <stddef.h>
#include <stdint.h>
struct open_cfw_ring_control {uint8_t connection_id,handler_id;uint16_t reserved;uint16_t *handles;uint16_t connection_epoch;};
struct open_cfw_ring_message {uint16_t parameter;uint8_t event,status;const uint8_t *data;uint16_t length,handle;};
struct open_cfw_ring_control open_cfw_test_ring_control;
const uint8_t open_cfw_test_ring_uuid[16]={0x1f,0x9d,0x32,0xf7,0xf1,0x3a,0x65,0x8e,0x03,0x45,0x05,0x4f,0x01,0x00,0xe8,0xba};
const uint32_t open_cfw_test_ring_characteristics=0x52494e47u;
static uint16_t handles[3];static uint32_t w[64];static struct open_cfw_ring_message msg;
void open_cfw_test_ring_reset(void){uint32_t i;for(i=0;i<64;i++)w[i]=0;for(i=0;i<3;i++)handles[i]=0;open_cfw_test_ring_control=(struct open_cfw_ring_control){0};open_cfw_test_ring_control.handles=handles;msg=(struct open_cfw_ring_message){0};w[8]=1;}
uint16_t *open_cfw_test_ring_handles(void){return handles;}
void open_cfw_test_ring_set(uint32_t i,uint32_t v){if(i==0)open_cfw_test_ring_control.connection_id=(uint8_t)v;else if(i==1)open_cfw_test_ring_control.handler_id=(uint8_t)v;else if(i==2)open_cfw_test_ring_control.connection_epoch=(uint16_t)v;else if(i>=3&&i<=5)handles[i-3]=(uint16_t)v;else if(i<64)w[i]=v;}
uint32_t open_cfw_test_ring_word(uint32_t i){if(i==0)return open_cfw_test_ring_control.connection_id;if(i==1)return open_cfw_test_ring_control.handler_id;if(i==2)return open_cfw_test_ring_control.connection_epoch;if(i>=3&&i<=5)return handles[i-3];return i<64?w[i]:0;}
uint8_t open_cfw_test_ring_in_use(uint8_t i){w[6]++;w[7]=i;return (uint8_t)w[8];}
void open_cfw_test_ring_write_request(uint8_t i,uint16_t h,uint16_t n,const uint8_t*d){w[9]++;w[10]=i;w[11]=h;w[12]=n;w[13]=d?d[0]:0;}
void open_cfw_test_ring_discover(uint8_t i,uint8_t un,const uint8_t*u,uint8_t hn,const void*c,uint16_t*h){w[40]++;w[41]=i;w[42]=un;w[43]=u?u[0]:0;w[44]=hn;w[45]=(c==&open_cfw_test_ring_characteristics);w[46]=(h==handles);}
uint8_t open_cfw_test_ring_role(uint8_t i){w[14]++;w[15]=i;return (uint8_t)w[16];}
void open_cfw_test_ring_write_command(uint8_t i,uint16_t h,uint16_t n,const uint8_t*d){w[25]++;w[26]=i;w[27]=h;w[28]=n;w[29]=d?d[0]:0;}
uint8_t open_cfw_test_ring_remove(void(*c)(void*)){w[17]++;w[47]=(c!=NULL);return 1;}
void open_cfw_test_ring_push(void(*c)(void*),void*a,uint32_t d){uint32_t n=w[18]++;if(n<3){w[48+n]=(uint32_t)(uintptr_t)a;w[51+n]=d;}w[54]=(c!=NULL);}
void open_cfw_test_ring_thread_event(uint32_t e){w[20]++;w[21]=e;}
void open_cfw_test_ring_thread_message(const uint8_t*d,uint16_t n){w[22]++;w[23]=n;w[24]=d?d[0]:0;}
void open_cfw_test_ring_wait(void){w[30]++;}
void open_cfw_test_ring_complete(void){w[38]++;}
void *open_cfw_test_ring_alloc(uint16_t n){w[31]++;w[32]=n;return w[39]?NULL:&msg;}
void open_cfw_test_ring_send(uint8_t h,void*m){struct open_cfw_ring_message*x=m;w[33]++;w[34]=h;w[35]=x->parameter;w[36]=x->event;w[37]=x->length;w[55]=(uint32_t)(uintptr_t)x->data;}
