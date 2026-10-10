#include <stdint.h>
#include <stddef.h>
#define ATTC_MSG_API_NONE 0
#define ATT_OPCODE_2_METHOD(x) ((x)/2)
#define ATT_METHOD_SIGNED_WRITE_CMD 17
#define ATT_METHOD_ERR 0
#define ATT_METHOD_MTU 1
#define L2C_PAYLOAD_START 8
#define ATT_HDR_LEN 1
#define ATT_SUCCESS 0
#define ATTC_NOT_CONTINUING 0
#define ATT_CCB_STATUS_FLOW_DISABLED 2
#define ATT_BEARER_SLOT_ID 0
#define ATT_CHECK_DATA_LENGTH(l,m) if((l)<(m))return
struct hdr {uint16_t param;uint8_t event,status;};
typedef struct {struct hdr hdr;uint8_t*pPkt;uint16_t handle;} Msg;
typedef struct {struct hdr hdr;uint8_t*pValue;uint16_t valueLen,handle;uint8_t continuing;} attEvt_t;
struct Main {struct {uint8_t control;} sccb[3];};
typedef struct {struct Main*pMainCcb;Msg outReq;uint8_t outReqTimer[16],slot,connId;} attcCcb_t;
static struct {Msg onDeck[3];} attcCb;
static struct {void(*cback)(attEvt_t*);} attCb;
static uint32_t ev[32],cnt,selected;
static void rec(uint32_t x){ev[cnt++]=x;}
static void WsfTimerStop(void*p){rec(1);}
static void attcFreePkt(Msg*m){rec(3);m->pPkt=NULL;}
static void attcSendReq(attcCcb_t*c){rec(5);}
static void attcSetupReq(attcCcb_t*c,Msg*m){selected=(uint32_t)(m-attcCb.onDeck);rec(100+selected);}
static void process(attcCcb_t*c,uint16_t l,uint8_t*p,attEvt_t*e){rec(2);}
typedef void(*attcProcRsp_t)(attcCcb_t*,uint16_t,uint8_t*,attEvt_t*);
static attcProcRsp_t attcProcRspTbl[18]={[9]=process};
static uint8_t attcMinPduLen[18]={[9]=1};
void attcProcRsp(attcCcb_t *pCcb, uint16_t len, uint8_t *pPacket)
{
  attEvt_t      evt;
  attcProcRsp_t procFcn;

  /* if no request in progress ignore response */
  if (pCcb->outReq.hdr.event == ATTC_MSG_API_NONE)
  {
    return;
  }

  /* get method */
  evt.hdr.event = ATT_OPCODE_2_METHOD(*(pPacket + L2C_PAYLOAD_START));

  /* check the validity of event */
  if (evt.hdr.event > ATT_METHOD_SIGNED_WRITE_CMD)
  {
    return;
  }

  /* if response method is not error and does not match stored method ignore response */
  if ((evt.hdr.event != ATT_METHOD_ERR) && (evt.hdr.event != pCcb->outReq.hdr.event))
  {
    return;
  }

  /* stop request timer */
  WsfTimerStop(&pCcb->outReqTimer);

  /* initialize event structure then process response */
  evt.pValue = pPacket + L2C_PAYLOAD_START + ATT_HDR_LEN;
  evt.valueLen = len - ATT_HDR_LEN;
  evt.handle = pCcb->outReq.handle;
  evt.hdr.status = ATT_SUCCESS;

  /* look up processing function */
  procFcn = attcProcRspTbl[evt.hdr.event];

  /* if method is supported */
  if (procFcn != NULL)
  {
    /* check the validity of data length */
    ATT_CHECK_DATA_LENGTH(len, attcMinPduLen[evt.hdr.event]);

    /* execute processing function */
    (*procFcn)(pCcb, len, pPacket, &evt);

    procFcn = NULL;
  }

  /* if not continuing or status is not success */
  if ((pCcb->outReq.hdr.status == ATTC_NOT_CONTINUING) || (evt.hdr.status != ATT_SUCCESS))
  {
    /* we're not sending another request so clear the out req */
    pCcb->outReq.hdr.event = ATTC_MSG_API_NONE;
    attcFreePkt(&pCcb->outReq);
  }

  /* call callback (if not mtu rsp) */
  if ((evt.hdr.event != ATT_METHOD_MTU) && attCb.cback)
  {
    /* set additional parameters and call callback */
    evt.continuing = pCcb->outReq.hdr.status;   /* continuing flag */
    evt.hdr.param = pCcb->outReq.hdr.param;     /* connId */
    (*attCb.cback)(&evt);
  }

  /* if no flow control */
  if (!(pCcb->pMainCcb->sccb[pCcb->slot].control & ATT_CCB_STATUS_FLOW_DISABLED))
  {
    /* if out req ready */
    if (pCcb->outReq.pPkt != NULL)
    {
      /* build and send request */
      attcSendReq(pCcb);
    }
    /* else if api is on deck */
    else if ((pCcb->slot == ATT_BEARER_SLOT_ID) &&
             (attcCb.onDeck[pCcb->connId-1].hdr.event != ATTC_MSG_API_NONE))
    {
      /* set up and send request */
      attcSetupReq(pCcb, &attcCb.onDeck[pCcb->connId-1]);

      /* clear on deck */
      attcCb.onDeck[pCcb->connId-1].hdr.event = ATTC_MSG_API_NONE;
    }
  }
}
void test(uint8_t e0,uint8_t e1){cnt=0;selected=99;struct Main main={0};attcCcb_t c={0};uint8_t p[32]={0};p[8]=0x13;c.pMainCcb=&main;c.outReq.hdr.event=9;c.outReq.hdr.status=0;c.connId=1;c.slot=0;c.outReq.handle=0x234;attCb.cback=NULL;attcCb.onDeck[0].hdr.event=e0;attcCb.onDeck[1].hdr.event=e1;attcCb.onDeck[2].hdr.event=0;attcProcRsp(&c,1,p);}
uint32_t count(void){return cnt;}uint32_t event(uint32_t i){return ev[i];}uint32_t select_index(void){return selected;}uint32_t remaining(uint32_t i){return attcCb.onDeck[i].hdr.event;}
