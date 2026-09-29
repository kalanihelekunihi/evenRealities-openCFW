
undefined8 FUN_0045bc06(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_0045bff0;
  if ((*DAT_0045bff0 == 0) || (iVar2 = osMutexAcquire(*DAT_0045bff0,0), iVar2 != 0)) {
    *DAT_0045bff4 = 0;
  }
  else {
    *DAT_0045bff4 = 0;
    osMutexRelease(*piVar1);
  }
  iVar2 = FUN_0043d0ce();
  local_10 = param_3;
  local_c = param_4;
  if (iVar2 << 0x1e < 0) {
    local_c = DAT_0045bff8;
    local_10 = 0x2b3;
    FUN_0043d574(3,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,DAT_0045bffc);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__sync_module_framework_DispStart_0045c000,
                        PTR_s__sync_module_framework_DispStart_0045c000);
  }
  return CONCAT44(local_c,local_10);
}

