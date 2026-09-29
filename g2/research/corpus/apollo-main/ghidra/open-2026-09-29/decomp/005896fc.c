
undefined8 FUN_005896fc(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 uVar4;
  
  uVar4 = param_3;
  FUN_005893fe();
  iVar1 = DAT_00589934;
  if (*(byte *)(DAT_00589934 + 0xc2) < 0x10) {
    if ((param_1 == 0) && (param_2 == 0)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar4 = 0xf0;
        FUN_0043d574(2,DAT_00589944,DAT_00589940,DAT_00589978,0xf0,DAT_00589980);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00589984,DAT_00589984);
      }
      uVar2 = 0;
    }
    else {
      *(int *)(DAT_00589934 + (uint)*(byte *)(DAT_00589934 + 0xc1) * 0xc) = param_1;
      *(int *)((uint)*(byte *)(iVar1 + 0xc1) * 0xc + iVar1 + 4) = param_2;
      *(undefined4 *)((uint)*(byte *)(iVar1 + 0xc1) * 0xc + iVar1 + 8) = param_3;
      uVar3 = *(byte *)(iVar1 + 0xc1) + 1;
      *(char *)(iVar1 + 0xc1) = (char)uVar3 + (char)(uVar3 / 0x10) * -0x10;
      *(char *)(iVar1 + 0xc2) = *(char *)(iVar1 + 0xc2) + '\x01';
      if (*(char *)(iVar1 + 0xc3) == '\0') {
        FUN_0058956e();
      }
      uVar2 = 1;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar4 = 0xea;
      FUN_0043d574(2,DAT_00589944,DAT_00589940,DAT_00589978,0xea,DAT_00589974);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0058997c,DAT_0058997c);
    }
    uVar2 = 0;
  }
  return CONCAT44(uVar4,uVar2);
}

