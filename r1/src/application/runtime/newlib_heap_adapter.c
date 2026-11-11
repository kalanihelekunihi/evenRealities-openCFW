/* Newlib allocations share the canonical native FreeRTOS heap. Only this
 * adapter's allocations carry its size header; ordinary pvPortMalloc users
 * keep their existing layout. Native heap exhaustion remains fatal. */
#include <stddef.h>
#include <stdint.h>
#include <errno.h>
#include <reent.h>
#include <string.h>
extern void *pvPortMalloc(uint32_t);
extern void vPortFree(void *);
union allocation_header { max_align_t alignment;size_t requested; };
_Static_assert(sizeof(size_t)==4 && _Alignof(max_align_t)<=8 &&
               sizeof(union allocation_header)%8==0,
               "native heap provides eight-byte aligned allocations");
static void no_memory(struct _reent *context)
{
    if (context) context->_errno=ENOMEM;
}
void *_malloc_r(struct _reent *context,size_t size)
{
    if (!size) return NULL;
    /* The native allocator adds at most 24 bytes and rejects signed sizes.
     * Reject arithmetic-invalid requests before its fatal allocation path. */
    if (size>INT32_MAX-sizeof(union allocation_header)-24u) {
        no_memory(context);return NULL;
    }
    union allocation_header *header=pvPortMalloc(
        (uint32_t)(size+sizeof(union allocation_header)));
    if (!header) {no_memory(context);return NULL;}
    header->requested=size;
    return header+1;
}
void _free_r(struct _reent *context,void *pointer)
{
    (void)context;
    if (pointer) vPortFree((union allocation_header *)pointer-1);
}
void *_calloc_r(struct _reent *context,size_t count,size_t size)
{
    if (size && count>SIZE_MAX/size) {no_memory(context);return NULL;}
    size_t total=count*size;
    void *pointer=_malloc_r(context,total);
    if (pointer) memset(pointer,0,total);
    return pointer;
}
void *_realloc_r(struct _reent *context,void *pointer,size_t size)
{
    if (!pointer) return _malloc_r(context,size);
    if (!size) {_free_r(context,pointer);return NULL;}
    union allocation_header *header=(union allocation_header *)pointer-1;
    size_t previous=header->requested;
    if (size==previous) return pointer;
    void *replacement=_malloc_r(context,size);
    if (!replacement) return NULL;
    memcpy(replacement,pointer,previous<size?previous:size);
    _free_r(context,pointer);
    return replacement;
}
