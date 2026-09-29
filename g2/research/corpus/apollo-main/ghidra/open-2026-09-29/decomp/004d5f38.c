
void _printAppWhiteListInfo(byte *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  if (param_1 == (byte *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,0xc0,DAT_004d679c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004d67a4);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,0xc5,DAT_004d67a8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004d67ac,DAT_004d67ac);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,0xc6,DAT_004d67b0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004d67b4,DAT_004d67b4);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = DAT_004d6a44;
      if ((int)((uint)*param_1 << 0x1f) < 0) {
        uVar2 = DAT_004d6a40;
      }
      FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,199,DAT_004d6a1c,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = DAT_004d6a44;
      if ((int)((uint)*param_1 << 0x1f) < 0) {
        uVar2 = DAT_004d6a40;
      }
      compress_log_output(0x10400000,DAT_004d6a48,DAT_004d6a48,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = DAT_004d6a44;
      if ((*param_1 & 3) >> 1 != 0) {
        uVar2 = DAT_004d6a40;
      }
      FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,200,DAT_004d6a4c,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = DAT_004d6a44;
      if ((*param_1 & 3) >> 1 != 0) {
        uVar2 = DAT_004d6a40;
      }
      compress_log_output(0x10400000,DAT_004d6a54,DAT_004d6a54,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = DAT_004d6a44;
      if ((*param_1 & 0xf) >> 3 != 0) {
        uVar2 = DAT_004d6a40;
      }
      FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,0xc9,DAT_004d6a58,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = DAT_004d6a44;
      if ((*param_1 & 0xf) >> 3 != 0) {
        uVar2 = DAT_004d6a40;
      }
      compress_log_output(0x10400000,DAT_004d6ac0,DAT_004d6ac0,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = DAT_004d6a44;
      if ((*param_1 & 7) >> 2 != 0) {
        uVar2 = DAT_004d6a40;
      }
      FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,0xca,DAT_004d6ac4,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = DAT_004d6a44;
      if ((*param_1 & 7) >> 2 != 0) {
        uVar2 = DAT_004d6a40;
      }
      compress_log_output(0x10400000,DAT_004d6ac8,DAT_004d6ac8,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = DAT_004d6a44;
      if ((*param_1 & 0x1f) >> 4 != 0) {
        uVar2 = DAT_004d6a40;
      }
      FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,0xcb,DAT_004d6acc,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = DAT_004d6a44;
      if ((*param_1 & 0x1f) >> 4 != 0) {
        uVar2 = DAT_004d6a40;
      }
      compress_log_output(0x10400000,DAT_004d6ad0,DAT_004d6ad0,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,0xce,DAT_004d6ad4,param_1[1]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d6ad8,DAT_004d6ad8,param_1[1]);
    }
    for (iVar1 = 0; iVar1 < (int)(uint)param_1[1]; iVar1 = iVar1 + 1) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,0xd0,DAT_004d6adc,iVar1 + 1,
                     param_1 + iVar1 * 0x50 + 2,param_1 + iVar1 * 0x50 + 0x42);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_004d6ae0,DAT_004d6ae0,iVar1 + 1,
                            param_1 + iVar1 * 0x50 + 2,param_1 + iVar1 * 0x50 + 0x42);
      }
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d67a0,0xd2,DAT_004d6ae4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004d6ae8,DAT_004d6ae8);
    }
  }
  return;
}

