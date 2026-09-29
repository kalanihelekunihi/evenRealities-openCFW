
undefined8 FUN_0045baf0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if ((*DAT_0045bfb8 != 0) && (iVar1 = osMutexAcquire(*DAT_0045bfb8,0xffffffff), iVar1 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x279;
      param_2 = DAT_0045bfd4;
      FUN_0043d574(1,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,DAT_0045bfd8,0x279,
                   DAT_0045bfd4,iVar1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0045bfdc,DAT_0045bfdc,iVar1);
    }
  }
  return CONCAT44(param_2,param_1);
}

