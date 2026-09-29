
undefined4
terminal_request_display
          (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 local_18 [4];
  undefined4 local_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    local_18[0] = param_1;
    local_14 = param_2;
    if (*DAT_005e4784 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005e477c,DAT_005e4778,DAT_005e478c,0x61,DAT_005e4788);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_005e4790,DAT_005e4790);
      }
      uVar2 = 0;
    }
    else {
      uVar2 = FUN_00464bb2(0x30,local_18,8,0);
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

