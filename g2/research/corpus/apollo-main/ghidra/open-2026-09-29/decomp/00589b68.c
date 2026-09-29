
undefined4 FUN_00589b68(char param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  char local_14 [4];
  undefined4 local_10;
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    local_14[0] = param_1;
    local_10 = param_2;
    iVar1 = FUN_004434d0(6);
    if (iVar1 == 1) {
      if (param_1 == '\x12') {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = FUN_005540d6(0x12);
          FUN_0043d574(4,DAT_0058a320,DAT_0058a31c,DAT_0058a354,0x87,DAT_0058a350,0x12,uVar2,param_2
                      );
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          uVar2 = FUN_005540d6(0x12);
          compress_log_output(0x10c00000,DAT_0058a358,DAT_0058a358,0x12,uVar2,param_2);
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = FUN_005540d6(param_1);
          FUN_0043d574(3,DAT_0058a320,DAT_0058a31c,DAT_0058a354,0x89,DAT_0058a350,param_1,uVar2,
                       param_2);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          uVar2 = FUN_005540d6(param_1);
          compress_log_output(0xcc00000,DAT_0058a358,DAT_0058a358,param_1,uVar2,param_2);
        }
      }
      uVar2 = FUN_00464bb2(6,local_14,8,0);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0058a320,DAT_0058a31c,DAT_0058a354,0x8e,DAT_0058a35c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0058a360,DAT_0058a360);
      }
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

