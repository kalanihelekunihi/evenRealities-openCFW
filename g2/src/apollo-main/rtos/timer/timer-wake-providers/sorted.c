/* Offline C reconstruction of stock0x4560B2, not claimed verbatim upstream. */
#include "unlock.h"
void audio_public_list_insert(List_t *list,ListItem_t *item){
 ListItem_t *at;
 if(item->xItemValue==UINT32_MAX)at=list->xListEnd.pxPrevious;
 else{
  at=(ListItem_t *)&list->xListEnd;
  while(at->pxNext->xItemValue<=item->xItemValue)at=at->pxNext;
 }
 item->pxNext=at->pxNext;item->pxNext->pxPrevious=item;
 item->pxPrevious=at;at->pxNext=item;item->pxContainer=list;
 list->uxNumberOfItems++;
}
