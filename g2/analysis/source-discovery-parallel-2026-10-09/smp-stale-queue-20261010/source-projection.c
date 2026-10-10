#include <stdint.h>
#include <stddef.h>
typedef uint8_t wsfEventMask_t; typedef uint8_t wsfHandlerId_t;typedef uint8_t dmConnId_t;
typedef struct{uint16_t param;uint8_t event,status;}wsfMsgHdr_t;
typedef struct{uint8_t connId,token;}smpCcb_t;typedef wsfMsgHdr_t smpMsg_t;
typedef struct{wsfMsgHdr_t hdr;void*pPlainText;}secCmacMsg_t;
typedef struct{uint32_t id;}secQueueBuf_t;
typedef struct{secQueueBuf_t entries[4];uint32_t pos,n;}Queue;
typedef struct{Queue aesEncQueue;}secCb_t;secCb_t secCb;
static smpCcb_t ccb;static uint32_t events[32],count;
#define SMP_DB_SERVICE_IND 32
#define SMP_MSG_WSF_CMAC_CMPL 28
#define SMP_MSG_WSF_AES_CMPL 11
#define DM_CONN_ID_NONE 0
#define SMP_TRACE_WARN2(...) ((void)0)
static void rec(uint32_t x){events[count++]=x;}
static void SmpDbService(void){rec(900);}
static void WsfBufFree(void*p){rec(901);}
static smpCcb_t*smpCcbByConnId(dmConnId_t x){return &ccb;}
static void smpSmExecute(smpCcb_t*c,smpMsg_t*m){rec(500);}
static void*WsfMsgDeq(Queue*q,wsfHandlerId_t*h){rec(100);if(q->pos==q->n)return NULL;*h=(uint8_t)q->entries[q->pos].id;return &q->entries[q->pos++];}
static void WsfMsgFree(secQueueBuf_t*p){rec(200+p->id);}
void SmpHandler(wsfEventMask_t event, wsfMsgHdr_t *pMsg)
{
  smpCcb_t     *pCcb;

  /* Handle message */
  if (pMsg != NULL)
  {
    if (pMsg->event == SMP_DB_SERVICE_IND)
    {
      SmpDbService();
    }
    else
    {
      if (pMsg->event == SMP_MSG_WSF_CMAC_CMPL)
      {
        secCmacMsg_t *pCmac = (secCmacMsg_t *) pMsg;

        /* Free the plain text buffer that was allocated and passed into SecCmac */
        if (pCmac->pPlainText)
        {
          WsfBufFree(pCmac->pPlainText);
        }
      }

      /* get connection control block */
      pCcb = smpCcbByConnId((dmConnId_t) pMsg->param);

      /* verify connection is open */
      if (pCcb->connId != DM_CONN_ID_NONE)
      {
        /* if AES result verify it is not stale */
        if (pMsg->event == SMP_MSG_WSF_AES_CMPL && pCcb->token != pMsg->status)
        {
            extern secCb_t secCb;
            wsfHandlerId_t  handlerId = 0;
            secQueueBuf_t *pBuf = NULL;

            SMP_TRACE_WARN2("AES token mismatch: %d %d", pCcb->token, pMsg->status);

            while((pBuf=WsfMsgDeq(&secCb.aesEncQueue, &handlerId))!=NULL)
            {
                WsfMsgFree(pBuf);
            }
        }
        else
        {
          /* send to state machine */
          smpSmExecute(pCcb, (smpMsg_t *) pMsg);
        }
      }
    }
  }
  /* Handle events */
  else if (event)
  {

  }
}
void test(uint8_t token,uint8_t status,uint8_t conn,uint32_t n){count=0;secCb.aesEncQueue.pos=0;secCb.aesEncQueue.n=n;for(uint32_t i=0;i<n;i++)secCb.aesEncQueue.entries[i].id=i;ccb.connId=conn;ccb.token=token;wsfMsgHdr_t msg={1,11,status};SmpHandler(0,&msg);}
uint32_t event_count(void){return count;}uint32_t event_at(uint32_t i){return events[i];}uint32_t remaining(void){return secCb.aesEncQueue.n-secCb.aesEncQueue.pos;}
