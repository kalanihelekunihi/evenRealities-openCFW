#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
typedef uint8_t wsfHandlerId_t;
typedef struct {uint16_t param;uint8_t event,status;} Header;
typedef struct {Header hdr;struct{uint8_t randNum[8];}leRandCmdCmpl;struct{uint8_t data[16];}leEncryptCmdCmpl;} hciEvt_t;
typedef struct {uint32_t id;uint8_t type;} secQueueBuf_t;
typedef struct {secQueueBuf_t nodes[8];uint32_t n,pos,id;} Queue;
static struct {uint8_t rand[32],randTop;Queue pubKeyQueue,dhKeyQueue,aesEncQueue;void(*hciCbackTbl[8])(secQueueBuf_t*,hciEvt_t*,wsfHandlerId_t);}secCb;
static uint32_t events[128],count;
#define HCI_LE_RAND_CMD_CMPL_CBACK_EVT 28
#define HCI_LE_ENCRYPT_CMD_CMPL_CBACK_EVT 27
#define HCI_LE_READ_LOCAL_P256_PUB_KEY_CMPL_CBACK_EVT 37
#define HCI_LE_GENERATE_DHKEY_CMPL_CBACK_EVT 38
#define HCI_HW_ERROR_CBACK_EVT 20
#define HCI_RAND_LEN 8
#define SEC_HCI_RAND_MULT 4
#define SEC_TYPE_CCM 3
#define SEC_TYPE_CMAC 1
#define SEC_TYPE_AES_REV 4
#define HCI_ENCRYPT_DATA_LEN 16
#define WSF_ASSERT(x) do{if(!(x))abort();}while(0)
static void WStrReverse(void*p,uint32_t n){abort();}
static void*WsfMsgDeq(Queue*q,wsfHandlerId_t*h){events[count++]=100+q->id;if(q->pos==q->n)return NULL;secQueueBuf_t*p=&q->nodes[q->pos++];*h=p->id;return p;}
static void WsfMsgFree(secQueueBuf_t*p){events[count++]=200+p->id;}
static void cb(secQueueBuf_t*p,hciEvt_t*e,wsfHandlerId_t h){events[count++]=900;}
static void secHciCback(hciEvt_t *pEvent)
{
  secQueueBuf_t *pBuf = NULL;
  wsfHandlerId_t handlerId = 0;

  /* Handle random number event. */
  switch (pEvent->hdr.event)
  {
  case HCI_LE_RAND_CMD_CMPL_CBACK_EVT:

    /* Copy new data to circular buffer of random data. */
    memcpy(&secCb.rand[HCI_RAND_LEN * secCb.randTop], pEvent->leRandCmdCmpl.randNum, HCI_RAND_LEN);
    secCb.randTop = (secCb.randTop >= SEC_HCI_RAND_MULT - 1) ? 0 : secCb.randTop + 1;
    break;

  case HCI_LE_ENCRYPT_CMD_CMPL_CBACK_EVT:
    pBuf = WsfMsgDeq(&secCb.aesEncQueue, &handlerId);
    if (pBuf != NULL)
    {
      if (pBuf->type == SEC_TYPE_CCM || pBuf->type == SEC_TYPE_CMAC || pBuf->type == SEC_TYPE_AES_REV)
      {
        WStrReverse(pEvent->leEncryptCmdCmpl.data, HCI_ENCRYPT_DATA_LEN);
      }
    }
    else
    {
      /* Should never happen */
      WSF_ASSERT(0);
    }
    break;

  case HCI_LE_READ_LOCAL_P256_PUB_KEY_CMPL_CBACK_EVT:
    pBuf = WsfMsgDeq(&secCb.pubKeyQueue, &handlerId);
    break;

  case HCI_LE_GENERATE_DHKEY_CMPL_CBACK_EVT:
    pBuf = WsfMsgDeq(&secCb.dhKeyQueue, &handlerId);
    break;

  default:
    break;
  }

  if (pBuf)
  {
    WSF_ASSERT(secCb.hciCbackTbl[pBuf->type]);
    secCb.hciCbackTbl[pBuf->type](pBuf, pEvent, handlerId);
  }
}
void test(uint32_t p,uint32_t d,uint32_t a){memset(&secCb,0,sizeof(secCb));count=0;Queue*qs[]={&secCb.pubKeyQueue,&secCb.dhKeyQueue,&secCb.aesEncQueue};uint32_t ns[]={p,d,a};for(uint32_t i=0;i<3;i++){qs[i]->id=i;qs[i]->n=ns[i];for(uint32_t k=0;k<ns[i];k++){qs[i]->nodes[k].id=i*10+k;qs[i]->nodes[k].type=0;} }for(uint32_t i=0;i<8;i++)secCb.hciCbackTbl[i]=cb;hciEvt_t evt={0};evt.hdr.event=20;secHciCback(&evt);}
uint32_t event_count(void){return count;}uint32_t event_at(uint32_t i){return events[i];}uint32_t remaining(uint32_t i){Queue*qs[]={&secCb.pubKeyQueue,&secCb.dhKeyQueue,&secCb.aesEncQueue};return qs[i]->n-qs[i]->pos;}
