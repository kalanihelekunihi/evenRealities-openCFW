
void RPC_OnboardingFlagReplyToPeer
               (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 local_14;
  undefined1 local_13;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_0043c0e4(&local_14,2,0);
  local_14 = 0xe;
  local_13 = param_1;
  FUN_00465480(0x10,&local_14,2,0,5);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047e624,DAT_0047e620,DAT_0047e660,0x8c,DAT_0047e65c,param_1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0047e664,DAT_0047e664,param_1);
  }
  return;
}

