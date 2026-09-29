
void RPC_OnboardingFlagSendToPeer(void)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 in_r3;
  undefined1 local_14;
  undefined1 local_13;
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  uVar1 = kvdbOnboardingConfigGet();
  FUN_0043c0e4(&local_14,2,0);
  local_14 = 0xd;
  local_13 = uVar1;
  FUN_00465480(0x10,&local_14,2,0,5);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047e624,DAT_0047e620,PTR_s_RPC_OnboardingFlagSendToPeer_0047e654,0x7f,
                 PTR_s_send_flag__d_to_peer_0047e650,uVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__onboarding_data_mgr_send_flag___0047e658,
                        PTR_s__onboarding_data_mgr_send_flag___0047e658,uVar1);
  }
  return;
}

