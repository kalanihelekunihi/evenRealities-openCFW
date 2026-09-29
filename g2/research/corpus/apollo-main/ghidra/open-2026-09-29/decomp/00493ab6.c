
undefined8 FUN_00493ab6(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar1 = FUN_0043d0ce();
    uVar3 = param_2;
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0xcb;
      FUN_0043d574(1,DAT_004940c0,DAT_004940bc,DAT_00494290,0xcb,DAT_0049428c,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00494294);
    }
    uVar2 = 0xffffffff;
  }
  else {
    FUN_00493d02(param_1);
    uVar3 = (uint)*(ushort *)(param_2 + 0x1558);
    iVar1 = FUN_00493722(param_1,param_2 + 8,*(undefined2 *)(param_2 + 4),param_2 + 0x155c,uVar3,
                         param_2 + 0x36a0,*(undefined2 *)(param_2 + 0x369c));
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xdb;
        FUN_0043d574(3,DAT_004940c0,DAT_004940bc,DAT_00494290,0xdb,DAT_004942a0,
                     *(undefined4 *)(param_1 + 0xc));
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004945e0,DAT_004945e0,*(undefined4 *)(param_1 + 0xc));
      }
      uVar2 = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xd6;
        FUN_0043d574(1,DAT_004940c0,DAT_004940bc,DAT_00494290,0xd6,DAT_00494298);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0049429c,DAT_0049429c);
      }
      FUN_00493d02(param_1);
      uVar2 = 0xffffffff;
    }
  }
  return CONCAT44(uVar3,uVar2);
}

