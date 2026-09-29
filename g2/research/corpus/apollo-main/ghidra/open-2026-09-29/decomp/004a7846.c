
void SVC_KvdbReadOnboardingConfig
               (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = SVC_KvdbBlobRead(DAT_004a78b4,DAT_004a789c,1,param_4,param_3,param_4);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004a78ac,DAT_004a78a8,DAT_004a78c8,0x5d,DAT_004a78c4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004a78cc);
    }
  }
  kvdbOnboardingConfigPointer(param_1);
  return;
}

