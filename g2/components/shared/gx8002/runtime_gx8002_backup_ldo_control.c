/* SPDX-License-Identifier: MIT */
/* Backup digital LDO control, package 0x40a34. All inputs read the
 * register; invalid controls return -1 without writing it. */
int open_cfw_gx8002_backup_ldo_control(unsigned int control)
{
    volatile unsigned int *reg = (volatile unsigned int *)0xa0005058;
    unsigned int value = *reg & 255u;
    switch (control) {
    case 0: value &= 251u; break;
    case 1: value = (value & 249u) | 4u; break;
    case 2: value = (value & 251u) | 6u; break;
    default: return -1;
    }
    *reg = value;
    return 0;
}
