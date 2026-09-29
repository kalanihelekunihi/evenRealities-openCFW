
undefined4 FUN_004dfff8(int param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  if ((*(int *)(param_1 + 0x14) != 0) &&
     (iVar1 = FUN_0043e2ea(*(undefined4 *)(param_1 + 0x14)), iVar1 != 0)) {
    iVar1 = FUN_00450566(*(undefined4 *)(param_1 + 0x14),PTR_FUN_004df9a2_1_004e02e4);
    if (iVar1 != 0) {
      iVar5 = *(int *)(iVar1 + 0x2c);
      iVar1 = FUN_0044e4aa(*(undefined4 *)(param_1 + 0x14));
      iVar2 = FUN_0044e4bc(*(undefined4 *)(param_1 + 0x14));
      iVar2 = iVar2 + iVar1;
      iVar6 = iVar2 - iVar5;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b28,0x282,DAT_004e0b40,param_2,iVar5,iVar2
                     ,iVar6,iVar5);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x11400000,DAT_004e0b44,DAT_004e0b44,param_2,iVar5,iVar2,iVar6,iVar5);
      }
      if (param_2 == '\0') {
        iVar1 = -1;
      }
      else {
        iVar1 = 1;
      }
      if ((iVar1 < 1) || (2 < iVar6)) {
        if ((iVar1 < 0) && (iVar5 < 3)) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b28,0x28f,DAT_004e0b50);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_004e0b54,DAT_004e0b54);
          }
          uVar3 = 0;
        }
        else {
          iVar4 = FUN_004df97c(param_3,param_4);
          iVar6 = iVar4 * iVar1 + iVar5;
          if (iVar6 < 0) {
            iVar6 = 0;
          }
          else if (iVar2 < iVar6) {
            iVar6 = iVar2;
          }
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b28,0x2a1,DAT_004e0b58,iVar5,iVar6,
                         iVar4 * iVar1);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x10c00000,DAT_004e0b5c,DAT_004e0b5c,iVar5,iVar6,iVar4 * iVar1);
          }
          FUN_00450500(*(undefined4 *)(param_1 + 0x14),PTR_FUN_004df9a2_1_004e02e4);
          FUN_004dfb78(param_1,iVar6,200);
          uVar3 = 1;
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b28,0x289,DAT_004e0b48);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004e0b4c,DAT_004e0b4c);
        }
        uVar3 = 0;
      }
      return uVar3;
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b28,0x273,DAT_004e0b38);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004e0b3c,DAT_004e0b3c);
    }
    return 0;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,DAT_004e0b30,DAT_004e0b2c,DAT_004e0b28,0x26b,DAT_004e0b24);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x8000000,DAT_004e0b34,DAT_004e0b34);
  }
  *(undefined4 *)(param_1 + 0x14) = 0;
  return 0;
}

