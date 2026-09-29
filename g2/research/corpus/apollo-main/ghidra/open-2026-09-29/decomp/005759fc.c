
void pt_cmd_55_handler(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 local_14 [4];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00575e98,DAT_00575e94,DAT_005764f0,0xc6f,DAT_005764ec);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_005764f4,DAT_005764f4);
  }
  local_14[0] = 3;
  semantic_OtaFrameDispatch(0xc0,local_14,1);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00575e98,DAT_00575e94,DAT_005764f0,0xc72,DAT_005764f8,*DAT_005766f8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_005764fc,DAT_005764fc,*DAT_005766f8);
  }
  pt_handler_result(0x55,*DAT_005766f8,3,param_3,param_4);
  return;
}

