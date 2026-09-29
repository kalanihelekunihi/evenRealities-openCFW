
undefined4 FUN_005b02e4(undefined1 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 local_14 [4];
  undefined4 local_10;
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    local_14[0] = param_1;
    local_10 = param_2;
    iVar1 = FUN_004434d0(0xb);
    if (iVar1 == 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = FUN_005b16fc(param_1);
        FUN_0043d574(3,DAT_005b09f4,DAT_005b09f0,DAT_005b0a28,0x7e,DAT_005b0a24,param_1,uVar2,
                     param_2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        uVar2 = FUN_005b16fc(param_1);
        compress_log_output(0xcc00000,DAT_005b0a2c,DAT_005b0a2c,param_1,uVar2,param_2);
      }
      uVar2 = FUN_00464bb2(0xb,local_14,8,0);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005b09f4,DAT_005b09f0,DAT_005b0a28,0x82,DAT_005b0a30);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_005b0a34,DAT_005b0a34);
      }
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

