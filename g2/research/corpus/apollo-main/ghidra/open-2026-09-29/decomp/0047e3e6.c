
undefined8
OnboardingFlagSaveToFlash
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_0047e634;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_0047e634 != 1) goto LAB_0047e46e;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_c = DAT_0047e638;
    local_10 = 0x5c;
    FUN_0043d574(4,DAT_0047e624,DAT_0047e620,DAT_0047e63c);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0047e41c:
    compress_log_output(0x10000000,DAT_0047e640,DAT_0047e640);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0047e41c;
  }
  iVar2 = SVC_KvdbBlobWriteOnboardingConfig();
  if (iVar2 == 0) {
    *piVar1 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_c = DAT_0047e644;
      local_10 = 0x61;
      FUN_0043d574(1,DAT_0047e624,DAT_0047e620,DAT_0047e63c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0047e648);
    }
  }
LAB_0047e46e:
  return CONCAT44(local_c,local_10);
}

