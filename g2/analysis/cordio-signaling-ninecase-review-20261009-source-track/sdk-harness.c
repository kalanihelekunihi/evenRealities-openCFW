#include <stdint.h>
#include <stddef.h>
typedef uint8_t dmConnId_t;
#define DM_CONN_ID_NONE 0
#define DM_ROLE_MASTER 0
#define DM_ROLE_SLAVE 1
#define L2C_SIG_HDR_LEN 4
#define L2C_CHECK_DATA_LENGTH(len,min_len) if ((len)<(min_len)) return
static uint32_t events[64],count;
static uint8_t ci,rr;
static uint16_t ch,cl; static uintptr_t cp;
static void ev(uint32_t x){events[count++]=x;}
static dmConnId_t DmConnIdByHandle(uint16_t h){ev(0x10000000|h);return ci;}
static uint8_t DmConnRole(dmConnId_t c){ev(0x20000000|c);return rr;}
static void master(uint16_t h,uint16_t l,uint8_t *p){ev(0x30000000);ch=h;cl=l;cp=(uintptr_t)p;}
static void slave(uint16_t h,uint16_t l,uint8_t *p){ev(0x40000000);ch=h;cl=l;cp=(uintptr_t)p;}
#define L2C_TRACE_ERR1(fmt,role) ev(0x50000000|(role))
static struct {void (*masterRxSignalingPkt)(uint16_t,uint16_t,uint8_t*);void (*slaveRxSignalingPkt)(uint16_t,uint16_t,uint8_t*);} l2cCb;
void l2cRxSignalingPkt(uint16_t handle, uint16_t len, uint8_t *pPacket)
{
  uint8_t role;
  dmConnId_t connId;

  /* check the validity of data length */
  L2C_CHECK_DATA_LENGTH(len, L2C_SIG_HDR_LEN);

  if ((connId = DmConnIdByHandle(handle)) == DM_CONN_ID_NONE)
  {
    return;
  }

  role = DmConnRole(connId);

  if ((role == DM_ROLE_MASTER) && (l2cCb.masterRxSignalingPkt != NULL))
  {
    (*l2cCb.masterRxSignalingPkt)(handle, len, pPacket);
  }
  else if ((role == DM_ROLE_SLAVE) && (l2cCb.slaveRxSignalingPkt != NULL))
  {
    (*l2cCb.slaveRxSignalingPkt)(handle, len, pPacket);
  }
  else
  {
    L2C_TRACE_ERR1("Invalid role configuration: role=%d", role);
  }
}
void test(uint16_t h,uint16_t l,uint8_t*p,uint8_t c,uint8_t r,uint8_t cb){count=0;ci=c;rr=r;ch=cl=0;cp=0;l2cCb.masterRxSignalingPkt=cb?master:NULL;l2cCb.slaveRxSignalingPkt=cb?slave:NULL;l2cRxSignalingPkt(h,l,p);}
uint32_t event_count(void){return count;} uint32_t event_at(uint32_t i){return events[i];}
uint32_t callback_h(void){return ch;} uint32_t callback_l(void){return cl;} uintptr_t callback_p(void){return cp;}
