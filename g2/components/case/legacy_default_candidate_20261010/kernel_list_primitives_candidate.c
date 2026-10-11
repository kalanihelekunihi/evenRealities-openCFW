/* SPDX-License-Identifier: MIT
 * Kernel list operations from stock 0x0800bf2c, 0x0800bfb0 and
 * 0x0800bfe2. Fields are four-byte words in the retained scheduler ABI.
 */
#include <stdint.h>
static volatile uint32_t *words(uint32_t address)
{return (volatile uint32_t *)(uintptr_t)address;}

uint32_t case_kernel_list_remove(uint32_t item)
{
    volatile uint32_t *node=words(item),*list=words(node[4]);
    words(node[1])[2]=node[2];
    words(node[2])[1]=node[1];
    if(list[1]==item)list[1]=node[2];
    node[4]=0u;
    list[0]--;
    return list[0];
}

void case_kernel_list_insert_tail(uint32_t list,uint32_t item)
{
    volatile uint32_t *head=words(list),*node=words(item);
    uint32_t current=head[1];
    node[1]=current;
    node[2]=words(current)[2];
    words(words(current)[2])[1]=item;
    words(current)[2]=item;
    node[4]=list;
    head[0]++;
}

void case_kernel_list_insert_ordered(uint32_t list,uint32_t item)
{
    volatile uint32_t *head=words(list),*node=words(item);
    uint32_t before;
    if(node[0]==0xffffffffu)before=head[4];
    else{
        before=list+8u;
        while(words(words(before)[1])[0]<=node[0])before=words(before)[1];
    }
    uint32_t after=words(before)[1];
    node[1]=after;
    words(after)[2]=item;
    node[2]=before;
    words(before)[1]=item;
    node[4]=list;
    head[0]++;
}
