
void FUN_004abec8(void)

{
  int iVar1;
  undefined1 local_10;
  undefined1 local_f;
  undefined1 local_e;
  undefined1 local_d;
  
  FUN_0043c0e4(&local_10,5,0);
  local_10 = FUN_004acaa0();
  local_f = FUN_004acaac();
  local_e = FUN_004acab4();
  iVar1 = FUN_004acad0();
  local_d = iVar1 == 1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,DAT_004ac814,0x6b,DAT_004ac810,local_10,
                 local_f,local_e,local_d);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xd000000,DAT_004acaf8,DAT_004acaf8,local_10,local_f,local_e,local_d);
  }
  iVar1 = semantic_OtaTransferActive();
  if (iVar1 == 0) {
    APP_PbNotifyEncodeGlassesCaseInfo(0,&local_10);
  }
  return;
}

