
undefined8
service_ancc_message_count_get
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  
  piVar2 = DAT_00497938;
  if (*DAT_00497938 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0xb0;
      FUN_0043d574(1,DAT_00497948,DAT_00497944,DAT_00497d3c,0xb0,DAT_00497d28,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__svc_ancc_ANCC_message_mutex_not_00497d30,
                          PTR_s__svc_ancc_ANCC_message_mutex_not_00497d30);
    }
    uVar4 = 0;
  }
  else {
    iVar3 = osMutexAcquire(*DAT_00497938,0xffffffff);
    if (iVar3 == 0) {
      bVar1 = *DAT_00497d24;
      osMutexRelease(*piVar2);
      uVar4 = (uint)bVar1;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0xb5;
        FUN_0043d574(1,DAT_00497948,DAT_00497944,DAT_00497d3c,0xb5,DAT_00497d40);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00497d44,DAT_00497d44);
      }
      uVar4 = 0;
    }
  }
  return CONCAT44(param_2,uVar4);
}

