
undefined8 FUN_0045bb58(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if ((*DAT_0045bfb8 != 0) && (iVar1 = osMutexRelease(*DAT_0045bfb8), iVar1 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x285;
      param_2 = DAT_0045bfe0;
      FUN_0043d574(1,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,DAT_0045bfe4,0x285,
                   DAT_0045bfe0,iVar1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0045bfe8,DAT_0045bfe8,iVar1);
    }
  }
  return CONCAT44(param_2,param_1);
}

