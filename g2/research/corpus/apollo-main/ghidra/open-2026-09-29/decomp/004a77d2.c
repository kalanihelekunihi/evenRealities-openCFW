
undefined8
SVC_KvdbBlobWriteOnboardingConfig
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = SVC_KvdbBlobWrite(DAT_004a78b4,DAT_004a789c,1,param_4,param_3,param_4);
  if (iVar1 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x39;
      FUN_0043d574(1,DAT_004a78ac,DAT_004a78a8,DAT_004a78bc,0x39,DAT_004a78b8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004a78c0);
    }
  }
  return CONCAT44(param_3,iVar1);
}

