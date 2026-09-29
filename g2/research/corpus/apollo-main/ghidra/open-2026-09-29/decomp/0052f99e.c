
undefined4 FUN_0052f99e(int param_1,uint param_2)

{
  int iVar1;
  int *piVar2;
  uint uVar3;
  int *piVar4;
  
  uVar3 = 0;
  do {
    if (param_2 <= uVar3) {
      return 1;
    }
    if (*(int *)(uVar3 * 0x10 + DAT_0052ffc0 + 8) != 0) {
      piVar4 = (int *)(DAT_0052ffc0 + uVar3 * 0x10);
      iVar1 = piVar4[2];
      piVar2 = DAT_0052ffd8;
      if ((((iVar1 != 0x300000) && (piVar2 = DAT_0052fffc, iVar1 != DAT_0052ffcc)) &&
          (piVar2 = DAT_00530000, iVar1 != DAT_0052ffd0)) &&
         (piVar2 = DAT_0052ffdc, iVar1 != DAT_0052ffd4)) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0052ffec,0x132,DAT_00530004,piVar4[2],uVar3);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_00530008,DAT_00530008,piVar4[2],uVar3);
        }
        return 0;
      }
      *piVar2 = *piVar4 + param_1;
      piVar4[3] = *piVar2;
      iVar1 = DAT_0052ffe0;
      *(int *)(uVar3 * 0xc + DAT_0052ffe0 + 4) = piVar4[1];
      *(int *)(uVar3 * 0xc + iVar1 + 8) = piVar4[2];
      *(int *)(iVar1 + uVar3 * 0xc) = piVar4[3];
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0052ff50,DAT_0052ff4c,DAT_0052ffec,0x13e,DAT_0052ffe8,DAT_0052ffe4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0052fff0,DAT_0052fff0,DAT_0052ffe4);
      }
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0052ff50,DAT_0052ff4c,DAT_0052ffec,0x13f,DAT_0052fff4,uVar3,
                     **(undefined4 **)(DAT_0052ffe4 + uVar3 * 4),
                     *(undefined4 *)(*(int *)(DAT_0052ffe4 + uVar3 * 4) + 4),
                     *(undefined4 *)(*(int *)(DAT_0052ffe4 + uVar3 * 4) + 8));
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x11000000,DAT_0052fff8,DAT_0052fff8,uVar3,
                            **(undefined4 **)(DAT_0052ffe4 + uVar3 * 4),
                            *(undefined4 *)(*(int *)(DAT_0052ffe4 + uVar3 * 4) + 4),
                            *(undefined4 *)(*(int *)(DAT_0052ffe4 + uVar3 * 4) + 8));
      }
    }
    uVar3 = uVar3 + 1;
  } while( true );
}

