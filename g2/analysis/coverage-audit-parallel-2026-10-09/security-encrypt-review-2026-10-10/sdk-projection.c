#include <stdint.h>
#include <stddef.h>
#include <string.h>
typedef uint8_t wsfHandlerId_t;
typedef struct{uint16_t param;uint8_t event,status;}Hdr;
typedef union{Hdr hdr;struct{Hdr hdr;uint8_t status,data[16];}leEncryptCmdCmpl;struct{Hdr hdr;uint8_t status,randNum[8];}leRandCmdCmpl;}hciEvt_t;
typedef struct{uint8_t pad[52],type;}secQueueBuf_t;
typedef struct{int unused;}Queue;
typedef void(*CB)(secQueueBuf_t*,hciEvt_t*,wsfHandlerId_t);
static struct{uint8_t rand[32],randTop;Queue aesEncQueue,pubKeyQueue,dhKeyQueue;CB hciCbackTbl[5];}secCb;
static secQueueBuf_t buf;static hciEvt_t evt;static uint32_t events[16],count;static int empty;
#define HCI_LE_RAND_CMD_CMPL_CBACK_EVT 28
#define HCI_LE_ENCRYPT_CMD_CMPL_CBACK_EVT 27
#define HCI_LE_READ_LOCAL_P256_PUB_KEY_CMPL_CBACK_EVT 37
#define HCI_LE_GENERATE_DHKEY_CMPL_CBACK_EVT 38
#define HCI_HW_ERROR_CBACK_EVT 20
#define HCI_RAND_LEN 8
#define SEC_HCI_RAND_MULT 4
#define HCI_ENCRYPT_DATA_LEN 16
#define SEC_TYPE_CCM 3
#define SEC_TYPE_CMAC 1
#define SEC_TYPE_AES_REV 4
#define WSF_ASSERT(x) ((void)0)
static void*WsfMsgDeq(Queue*q,wsfHandlerId_t*h){events[count++]=100;*h=36;return empty?NULL:&buf;}
static void WsfMsgFree(void*p){events[count++]=400;}
static void WStrReverse(uint8_t*p,uint32_t n){events[count++]=200;for(uint32_t i=0;i<n/2;i++){uint8_t t=p[i];p[i]=p[n-1-i];p[n-1-i]=t;}}
static void callback(secQueueBuf_t*b,hciEvt_t*e,wsfHandlerId_t h){events[count++]=300+b->type;}
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

    WSF_ASSERT(pBuf != NULL);

    /* note: pBuf should never be NULL and is checked by assert above. */
    /* coverity[dereference] */
    if (pBuf->type == SEC_TYPE_CCM || pBuf->type == SEC_TYPE_CMAC || pBuf->type == SEC_TYPE_AES_REV)
    {
      WStrReverse(pEvent->leEncryptCmdCmpl.data, HCI_ENCRYPT_DATA_LEN);
    }
    break;

  case HCI_LE_READ_LOCAL_P256_PUB_KEY_CMPL_CBACK_EVT:
    pBuf = WsfMsgDeq(&secCb.pubKeyQueue, &handlerId);
    break;

  case HCI_LE_GENERATE_DHKEY_CMPL_CBACK_EVT:
    pBuf = WsfMsgDeq(&secCb.dhKeyQueue, &handlerId);
    break;

  case HCI_HW_ERROR_CBACK_EVT:
    while ((pBuf = WsfMsgDeq(&secCb.pubKeyQueue, &handlerId)) != NULL)
    {
      WsfMsgFree(pBuf);
    }

    while ((pBuf = WsfMsgDeq(&secCb.dhKeyQueue, &handlerId)) != NULL)
    {
      WsfMsgFree(pBuf);
    }

    while ((pBuf = WsfMsgDeq(&secCb.aesEncQueue, &handlerId)) != NULL)
    {
      WsfMsgFree(pBuf);
    }
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
void test(int type){count=0;empty=type<0;memset(&buf,0,sizeof(buf));memset(&evt,0,sizeof(evt));buf.type=type;evt.hdr.event=27;for(int i=0;i<16;i++)evt.leEncryptCmdCmpl.data[i]=i;for(int i=0;i<5;i++)secCb.hciCbackTbl[i]=callback;secHciCback(&evt);}
uint32_t event_count(void){return count;}uint32_t event_at(uint32_t i){return events[i];}uint32_t data_at(uint32_t i){return evt.leEncryptCmdCmpl.data[i];}
