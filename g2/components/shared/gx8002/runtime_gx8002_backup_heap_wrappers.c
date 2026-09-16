/* SPDX-License-Identifier: MIT */
/* Recovered LVP wrappers around the backup allocator. */
extern void rt_system_heap_init(void *, void *);
extern void *rt_malloc(unsigned int);
extern void *rt_calloc(unsigned int, unsigned int);
extern void *rt_realloc(void *, unsigned int);
extern void rt_free(void *);
int backup_heap_initialize(void)
{
    rt_system_heap_init((void *)0x2001bb80, (void *)0x2002cb80);
    return 0;
}
void *backup_allocate(unsigned int size) { return rt_malloc(size); }
void *backup_callocate(unsigned int count, unsigned int size) { return rt_calloc(count, size); }
void *backup_reallocate(void *pointer, unsigned int size) { return rt_realloc(pointer, size); }
int backup_free(void *pointer) { rt_free(pointer); return 0; }
