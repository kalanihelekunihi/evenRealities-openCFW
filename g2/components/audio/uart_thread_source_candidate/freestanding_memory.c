/* Main's freestanding C/ARM EABI byte-copy and clear runtime. */
#include <stddef.h>
#include <stdint.h>

void *memcpy(void *destination,const void *source,size_t bytes)
{
    volatile uint8_t *write=(volatile uint8_t *)destination;
    const volatile uint8_t *read=(const volatile uint8_t *)source;
    for (size_t i=0;i<bytes;++i) write[i]=read[i];
    return destination;
}

void *memset(void *destination,int value,size_t bytes)
{
    volatile uint8_t *write=(volatile uint8_t *)destination;
    for (size_t i=0;i<bytes;++i) write[i]=(uint8_t)value;
    return destination;
}

void __aeabi_memcpy(void *destination,const void *source,size_t bytes)
{
    (void)memcpy(destination,source,bytes);
}

void __aeabi_memclr(void *destination,size_t bytes)
{
    (void)memset(destination,0,bytes);
}

void __aeabi_memclr8(void *destination,size_t bytes)
{
    (void)memset(destination,0,bytes);
}
