
void RPC_OnboardingProcessSyncToPeer(void)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 in_r3;
  undefined1 local_10;
  undefined1 local_f;
  undefined1 local_e;
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(&local_10,3,0);
  puVar1 = DAT_0047e60c;
  local_10 = 9;
  local_f = *DAT_0047e60c;
  local_e = DAT_0047e60c[1];
  FUN_00465480(0x10,&local_10,3,0,5);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047e624,DAT_0047e620,DAT_0047e66c,0x9a,DAT_0047e668,*puVar1,puVar1[1]);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_0047e670,DAT_0047e670,*puVar1,puVar1[1]);
  }
  return;
}

