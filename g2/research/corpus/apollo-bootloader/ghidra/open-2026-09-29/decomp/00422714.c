
/* WARNING: Removing unreachable block (ram,0x00422798) */
/* WARNING: Removing unreachable block (ram,0x0042279c) */
/* WARNING: Removing unreachable block (ram,0x004227aa) */
/* WARNING: Removing unreachable block (ram,0x004227a0) */
/* WARNING: Removing unreachable block (ram,0x00422726) */

uint FUN_00422714(uint param_1)

{
  uint uVar1;
  uint uVar2;
  uint in_fpscr;
  undefined1 in_q0 [16];
  
  uVar1 = in_q0._4_4_ & 0xffff;
  if ((int)param_1 < 0) {
    uVar2 = 0;
    if (((in_q0._0_4_ & 0xffff) != 0 || uVar1 != 0) && (uVar2 = in_fpscr, 0x36 < -param_1)) {
LAB_004275d2:
      *DAT_004275e4 = 0x22;
      return 0;
    }
  }
  else {
    uVar1 = in_q0._0_4_ & 0xffff | uVar1 << 1;
    uVar2 = 0;
    if (uVar1 != 0) {
      if (param_1 < 0x3fc) {
        return 0;
      }
      if ((param_1 - 0x3f8) + (uint)(0x3f7 < param_1) < 0x7ff) {
        return uVar1;
      }
      goto LAB_004275d2;
    }
  }
  return uVar2;
}

