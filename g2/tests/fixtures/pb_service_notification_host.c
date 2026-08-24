#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static uint8_t decoded[0x4c],message[0x4c],buffer[0x100],encoded[0x4c],state[4];
static uint32_t decode_ok=1,encode_ok=1,command=1,magic=0x42,crc=0x12345678,crc_valid=1,tick=0x1ab;
static uint8_t payload[72];static uint32_t sent,kind,length,disabled,allocs,frees;
static uint32_t dec(void *,const void *,void *);static uint32_t enc(void *,const void *,const void *);
static int sendx(uint32_t,uint32_t,const void *,uint32_t);static int notifyx(uint32_t,uint32_t,const void *,uint32_t);
#define OPEN_CFW_PB_NOTIFICATION_DECODED_MESSAGE decoded
#define OPEN_CFW_PB_NOTIFICATION_MESSAGE message
#define OPEN_CFW_PB_NOTIFICATION_ENCODE_BUFFER buffer
#define OPEN_CFW_PB_NOTIFICATION_DESCRIPTOR ((const void *)(uintptr_t)0x7799f4U)
#define OPEN_CFW_PB_NOTIFICATION_INPUT_FROM_BUFFER(d,n) ((open_cfw_pb_notification_input){(void *)(d),0,(n),0})
#define OPEN_CFW_PB_NOTIFICATION_DECODE(i,d,m) dec((i),(d),(m))
#define OPEN_CFW_PB_NOTIFICATION_ENCODE(o,d,m) enc((o),(d),(m))
#define OPEN_CFW_PB_NOTIFICATION_SEND(r,s,d,n) sendx((r),(s),(d),(n))
#define OPEN_CFW_PB_NOTIFICATION_NOTIFY(r,s,d,n) notifyx((r),(s),(d),(n))
#define OPEN_CFW_PB_NOTIFICATION_CONTROL_STATE() state
#define OPEN_CFW_PB_NOTIFICATION_SET_WHITELIST_DISABLED(v) (disabled=(v))
#define OPEN_CFW_PB_NOTIFICATION_READ_WHITELIST_CRC(p) (*(p)=crc,(int)crc_valid)
#define OPEN_CFW_PB_NOTIFICATION_ALLOC(n) (++allocs,malloc(n))
#define OPEN_CFW_PB_NOTIFICATION_FREE(p) (++frees,free(p))
#define OPEN_CFW_PB_NOTIFICATION_TICK() tick
#include "../../components/apollo_main/core_overlay/pb_service_notification.c"
static uint32_t dec(void *ri,const void *d,void *rm){open_cfw_pb_notification_input *i=ri;uint8_t *m=rm;assert(d==OPEN_CFW_PB_NOTIFICATION_DESCRIPTOR);assert(i->bytes_left==4);if(!decode_ok)return 0;m[0]=(uint8_t)command;m[1]=(uint8_t)magic;memcpy(m+4,payload,sizeof(payload));return 1;}
static uint32_t enc(void *ro,const void *d,const void *m){open_cfw_pb_notification_output *o=ro;assert(d==OPEN_CFW_PB_NOTIFICATION_DESCRIPTOR);memcpy(encoded,m,sizeof(encoded));if(!encode_ok)return 0;o->length=17;return 1;}
static int tx(uint32_t k,uint32_t r,uint32_t s,const void *d,uint32_t n){assert(r==1&&s==4);assert(d!=0);sent++;kind=k;length=n;return k==2?0:7;}
static int sendx(uint32_t r,uint32_t s,const void *d,uint32_t n){return tx(1,r,s,d,n);}static int notifyx(uint32_t r,uint32_t s,const void *d,uint32_t n){return tx(2,r,s,d,n);}
static uint32_t u32(const uint8_t *p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void reset(void){memset(decoded,0,sizeof(decoded));memset(message,0,sizeof(message));memset(encoded,0,sizeof(encoded));memset(payload,0,sizeof(payload));memset(state,0,sizeof(state));decode_ok=encode_ok=crc_valid=1;command=1;magic=0x42;crc=0x12345678;tick=0x1ab;sent=kind=length=disabled=allocs=frees=0;}
int main(void){uint8_t in[4]={0};reset();assert(APP_PbRxNotificationFrameDataProcess(0,4)==2);decode_ok=0;assert(APP_PbRxNotificationFrameDataProcess(in,4)==0x2b);reset();payload[0]=1;payload[1]=2;payload[2]=3;payload[4]=4;assert(APP_PbRxNotificationFrameDataProcess(in,4)==0);assert(memcmp(state,(uint8_t[]){1,2,3,4},4)==0);assert(encoded[0]==1&&encoded[1]==0x42&&encoded[2]==3&&encoded[4]==1&&encoded[8]==4);assert(sent==1&&kind==1&&length==17);
reset();command=3;payload[0]=9;assert(APP_PbRxNotificationFrameDataProcess(in,4)==0);assert(disabled==1&&encoded[0]==3&&encoded[2]==6);
reset();command=4;payload[0]=0x78;payload[1]=0x56;payload[2]=0x34;payload[3]=0x12;assert(APP_PbRxNotificationFrameDataProcess(in,4)==0);assert(encoded[0]==4&&encoded[2]==7&&u32(encoded+4)==crc&&encoded[8]==2&&encoded[9]==0);reset();command=4;payload[0]=1;assert(APP_PbRxNotificationFrameDataProcess(in,4)==0&&encoded[8]==3);reset();command=4;crc_valid=0;assert(APP_PbRxNotificationFrameDataProcess(in,4)==0&&encoded[8]==1&&encoded[9]==7);
reset();command=99;assert(APP_PbRxNotificationFrameDataProcess(in,4)==0);assert(encoded[0]==0xa1&&encoded[2]==5&&encoded[4]==99&&encoded[5]==8);
reset();assert(APP_PbTxEncodeNotifAppIDNotInWhitelist("app.id","App")==0);assert(allocs==1&&frees==1&&sent==1&&kind==2);assert(encoded[0]==2&&encoded[1]==0xab&&encoded[2]==4);assert(encoded[4]==7&&strcmp((char *)encoded+6,"app.id")==0);assert(encoded[38]==4&&strcmp((char *)encoded+40,"App")==0);encode_ok=0;assert(APP_PbTxEncodeNotifAppIDNotInWhitelist("a","b")==0x2b&&allocs==2&&frees==2);return 0;}
