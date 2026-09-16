/* SPDX-License-Identifier: MIT */
/* Complete loader control recovered from package 0x396a0..0x39744.
 * Flash-helper return values are ignored in stock. The special mode's
 * second length argument is intentionally zero, not an inferred copy size. */
extern int open_cfw_gx8002_loader_flash_read(unsigned int offset,
                                          void *destination,
                                          unsigned int length);
int open_cfw_gx8002_backup_loader(void)
{
    unsigned int base = *(volatile unsigned int *)0x20001724;
    unsigned int header;
    unsigned int entry;
    if (*(volatile unsigned int *)0x20033ffc == 0xaabbccdd) {
        open_cfw_gx8002_loader_flash_read(base + 0x323b0, &header, 4);
        open_cfw_gx8002_loader_flash_read(header + 0x323b4,
                                        (void *)0x20000000, 0);
        entry = 0x10000100;
    } else {
        unsigned int offset = base + 0x3000;
        open_cfw_gx8002_loader_flash_read(offset, &header, 4);
        open_cfw_gx8002_loader_flash_read(offset + header + 4,
                                        (void *)0x10003000, 0x1408c);
        entry = 0x10003100;
    }
    *(volatile unsigned int *)0x2002d3e4 = entry;
    ((void (*)(void))entry)();
    return 0;
}
