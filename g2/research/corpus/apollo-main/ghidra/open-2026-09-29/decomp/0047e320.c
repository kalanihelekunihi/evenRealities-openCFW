
void onboarding_notify_wear_status_to_app
               (byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_1c;
  uint local_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar1 = semantic_OtaTransferActive();
  if (((iVar1 != 1) && (iVar1 = FUN_00443484(), iVar1 != 0)) &&
     (iVar1 = FUN_004434d0(0x10), iVar1 == 1)) {
    local_1c = *DAT_0047e614;
    uStack_14 = DAT_0047e614[2];
    local_18 = (uint)param_1;
    iVar1 = APP_PbNotifyEncodeOnboardingEvent(0,&local_1c);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047e624,DAT_0047e620,DAT_0047e61c,0x51,DAT_0047e618,param_1);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0047e628,DAT_0047e628,param_1);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0047e624,DAT_0047e620,DAT_0047e61c,0x53,DAT_0047e62c,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0047e630,DAT_0047e630,iVar1);
      }
    }
  }
  return;
}

