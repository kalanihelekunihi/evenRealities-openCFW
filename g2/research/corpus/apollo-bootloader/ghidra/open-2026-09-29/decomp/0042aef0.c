
undefined4 spotmgr_buck_deepsleep_scan_42aef0(uint *param_1)

{
  bool bVar1;
  byte bVar2;
  int iVar3;
  uint uVar4;
  undefined4 unaff_r7;
  
  if (((((char)param_1[4] == '\x03') || ((*param_1 & 0x3fffffff) != 0)) ||
      ((param_1[1] & 0x4c4) != 0)) || (*DAT_0042b9d4 << 2 < 0)) {
    *DAT_0042b9d8 = 1;
  }
  else {
    iVar3 = FUN_0041f3f0();
    if (((iVar3 == 0) || ((*DAT_0042b9dc & 0xf) == 0)) || (2 < (*DAT_0042b9dc & 0xf))) {
      for (uVar4 = 0; uVar4 < 0x10; uVar4 = uVar4 + 1) {
        if ((*(int *)(DAT_0042b9e0 + uVar4 * 0x20 + 0x200) << 0x1f < 0) &&
           ((int)((*DAT_0042b9e4 >> (uVar4 & 0xff)) << 0x1f) < 0)) {
          if ((*(uint *)(DAT_0042b9e0 + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8 < 6) {
LAB_0042afec:
            bVar2 = 0;
          }
          else {
            if (((*(uint *)(DAT_0042b9e0 + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8 < 0x13) ||
               (0x18 < (*(uint *)(DAT_0042b9e0 + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8)) {
              bVar1 = false;
            }
            else {
              bVar1 = true;
            }
            if (bVar1) goto LAB_0042afec;
            if (((*(uint *)(DAT_0042b9e0 + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8 < 0x100) ||
               (0x1df < (*(uint *)(DAT_0042b9e0 + uVar4 * 0x20 + 0x200) & 0x1ffff) >> 8)) {
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
          *DAT_0042b9d8 = 1;
          return unaff_r7;
        }
      }
      *DAT_0042b9d8 = 0;
    }
    else {
      *DAT_0042b9d8 = 1;
    }
  }
  return unaff_r7;
}

