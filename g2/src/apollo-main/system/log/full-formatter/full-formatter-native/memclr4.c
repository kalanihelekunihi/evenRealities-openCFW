/* ARM EABI memset-to-zero compiler helper used by the pinned IAR-model C.
 * Same byte-zero implementation as the qualified Bootloader source unit. */
void __aeabi_memclr4(void *destination,unsigned bytes) {
    volatile unsigned char *p=(volatile unsigned char *)destination;
    while(bytes--) *p++=0u;
}
