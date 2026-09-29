
undefined8 service_ancc_record_find(byte param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  byte bVar3;
  
  piVar1 = DAT_00497938;
  if (*DAT_00497938 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0xc5;
      FUN_0043d574(1,DAT_00497948,DAT_00497944,DAT_00497d48,0xc5,DAT_00497d28);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__svc_ancc_ANCC_message_mutex_not_00497d30,
                          PTR_s__svc_ancc_ANCC_message_mutex_not_00497d30);
    }
    iVar2 = 0;
  }
  else {
    iVar2 = osMutexAcquire(*DAT_00497938,0xffffffff);
    if (iVar2 == 0) {
      if (param_1 < *DAT_00497d24) {
        iVar2 = *DAT_0049795c;
        if (iVar2 == 0) {
          osMutexRelease(*piVar1);
          iVar2 = 0;
        }
        else {
          for (bVar3 = 0; bVar3 < param_1; bVar3 = bVar3 + 1) {
            if (*(int *)(iVar2 + 0x300) == 0) {
              osMutexRelease(*piVar1);
              iVar2 = 0;
              goto LAB_00497694;
            }
            iVar2 = *(int *)(iVar2 + 0x300);
          }
          osMutexRelease(*piVar1);
        }
      }
      else {
        osMutexRelease(*piVar1);
        iVar2 = 0;
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0xca;
        FUN_0043d574(1,DAT_00497948,DAT_00497944,DAT_00497d48,0xca,DAT_00497d4c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00497d50);
      }
      iVar2 = 0;
    }
  }
LAB_00497694:
  return CONCAT44(param_3,iVar2);
}

