
undefined4 FUN_005a0204(void)

{
  bool bVar1;
  byte bVar2;
  int iVar3;
  uint uVar4;
  undefined4 unaff_r7;
  
  if (*DAT_005a09e8 != '\0') {
    if (*DAT_005a09dc == '\x02') {
      *DAT_005a09ec = 1;
    }
    else {
      iVar3 = FUN_0048d620();
      if (((iVar3 == 0) || ((*DAT_005a09f8 & 0xf) == 0)) || (2 < (*DAT_005a09f8 & 0xf))) {
        for (uVar4 = 0; uVar4 < 0x10; uVar4 = uVar4 + 1) {
          if ((*(int *)(DAT_005a09fc + uVar4 * 0x20 + 0x200) << 0x1f < 0) &&
             ((int)((*DAT_005a0a00 >> (uVar4 & 0xff)) << 0x1f) < 0)) {
            if ((*(uint *)(DAT_005a09fc + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8 < 6) {
LAB_005a02f2:
              bVar2 = 0;
            }
            else {
              if (((*(uint *)(DAT_005a09fc + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8 < 0x13) ||
                 (0x18 < (*(uint *)(DAT_005a09fc + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8)) {
                bVar1 = false;
              }
              else {
                bVar1 = true;
              }
              if (bVar1) goto LAB_005a02f2;
              if (((*(uint *)(DAT_005a09fc + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8 < 0x100) ||
                 (0x1df < (*(uint *)(DAT_005a09fc + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8)) {
                bVar2 = 0;
              }
              else {
                bVar2 = 1;
              }
              bVar2 = bVar2 ^ 1;
            }
            bVar1 = (bool)(bVar2 ^ 1);
          }
          else {
            bVar1 = false;
          }
          if (bVar1) {
            *DAT_005a09ec = 1;
            return unaff_r7;
          }
        }
        *DAT_005a09ec = 0;
      }
      else {
        *DAT_005a09ec = 1;
      }
    }
  }
  return unaff_r7;
}

