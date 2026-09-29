
undefined4 FUN_00472596(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00472bbc,DAT_00472bb8,DAT_00472be4,0x1b8,DAT_00472be0,param_1,4,1,2,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xd000000,DAT_00472be8,DAT_00472be8,param_1,4,1,2);
  }
  DmSetPhy(param_1,0,4,1,2);
  return 0;
}

