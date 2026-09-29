
undefined8
service_ancc_record_remove(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  byte *pbVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  byte bVar6;
  
  piVar1 = DAT_00497938;
  if (param_1 != 0) {
    if (*DAT_00497938 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x137;
        param_3 = DAT_00497d28;
        FUN_0043d574(1,DAT_00497948,DAT_00497944,DAT_00497d60,0x137,DAT_00497d28,param_4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__svc_ancc_ANCC_message_mutex_not_00497d30,
                            PTR_s__svc_ancc_ANCC_message_mutex_not_00497d30);
      }
    }
    else {
      iVar3 = osMutexAcquire(*DAT_00497938,0xffffffff);
      pbVar2 = DAT_00497d24;
      if (iVar3 == 0) {
        iVar3 = *DAT_0049795c;
        iVar5 = 0;
        for (bVar6 = 0; (iVar4 = iVar3, iVar4 != 0 && (bVar6 < *DAT_00497d24)); bVar6 = bVar6 + 1) {
          if (iVar4 == param_1) {
            if (iVar5 == 0) {
              *DAT_0049795c = *(int *)(iVar4 + 0x300);
            }
            else {
              *(undefined4 *)(iVar5 + 0x300) = *(undefined4 *)(iVar4 + 0x300);
            }
            *(undefined1 *)(iVar4 + 0x2fc) = 0;
            *(undefined4 *)(iVar4 + 0x300) = 0;
            *pbVar2 = *pbVar2 - 1;
            bVar6 = *pbVar2;
            osMutexRelease(*piVar1);
            CB_ANCC_NotifyMsgCount(0,bVar6);
            goto LAB_00497936;
          }
          iVar3 = *(int *)(iVar4 + 0x300);
          iVar5 = iVar4;
        }
        osMutexRelease(*piVar1);
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          param_2 = 0x13c;
          param_3 = DAT_00497d64;
          FUN_0043d574(1,DAT_00497948,DAT_00497944,DAT_00497d60);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00497d68);
        }
      }
    }
  }
LAB_00497936:
  return CONCAT44(param_3,param_2);
}

