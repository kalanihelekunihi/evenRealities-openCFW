
undefined8 FUN_0045ba46(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_0045bfb8;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_0045bfb8 == 0) {
    iVar2 = osMutexNew(PTR_DAT_0045bfbc);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_c = PTR_DAT_0045bfc0;
        local_10 = 0x26b;
        FUN_0043d574(1,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                     PTR_s_initGlobalVariableMutex_0045bfc4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_DAT_0045bfc8,PTR_DAT_0045bfc8);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_c = PTR_DAT_0045bfcc;
        local_10 = 0x26d;
        FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,
                     PTR_s_initGlobalVariableMutex_0045bfc4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_DAT_0045bfd0,PTR_DAT_0045bfd0);
      }
    }
  }
  return CONCAT44(local_c,local_10);
}

