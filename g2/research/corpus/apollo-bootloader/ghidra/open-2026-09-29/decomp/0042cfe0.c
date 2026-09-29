
undefined4 state_event_zero_42cfe0(void)

{
  bool bVar1;
  byte bVar2;
  int iVar3;
  uint uVar4;
  undefined4 unaff_r7;
  
  if (*DAT_0042d7c4 != '\0') {
    if (*DAT_0042d7b8 == '\x02') {
      *DAT_0042d7c8 = 1;
    }
    else {
      iVar3 = FUN_0041f3f0();
      if (((iVar3 == 0) || ((*DAT_0042d7d4 & 0xf) == 0)) || (2 < (*DAT_0042d7d4 & 0xf))) {
        for (uVar4 = 0; uVar4 < 0x10; uVar4 = uVar4 + 1) {
          if ((*(int *)(DAT_0042d7d8 + uVar4 * 0x20 + 0x200) << 0x1f < 0) &&
             ((int)((*DAT_0042d7dc >> (uVar4 & 0xff)) << 0x1f) < 0)) {
            if ((*(uint *)(DAT_0042d7d8 + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8 < 6) {
LAB_0042d0ce:
              bVar2 = 0;
            }
            else {
              if (((*(uint *)(DAT_0042d7d8 + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8 < 0x13) ||
                 (0x18 < (*(uint *)(DAT_0042d7d8 + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8)) {
                bVar1 = false;
              }
              else {
                bVar1 = true;
              }
              if (bVar1) goto LAB_0042d0ce;
              if (((*(uint *)(DAT_0042d7d8 + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8 < 0x100) ||
                 (0x1df < (*(uint *)(DAT_0042d7d8 + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8)) {
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
            *DAT_0042d7c8 = 1;
            return unaff_r7;
          }
        }
        *DAT_0042d7c8 = 0;
      }
      else {
        *DAT_0042d7c8 = 1;
      }
    }
  }
  return unaff_r7;
}

