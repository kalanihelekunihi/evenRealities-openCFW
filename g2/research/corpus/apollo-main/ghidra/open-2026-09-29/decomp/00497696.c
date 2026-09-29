
undefined8 service_ancc_record_allocate(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  char cVar1;
  int *piVar2;
  int *piVar3;
  char *pcVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  piVar2 = DAT_00497938;
  if (*DAT_00497938 == 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      param_3 = 0xeb;
      FUN_0043d574(1,DAT_00497948,DAT_00497944,DAT_00497d54,0xeb,DAT_00497d28);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__svc_ancc_ANCC_message_mutex_not_00497d30,
                          PTR_s__svc_ancc_ANCC_message_mutex_not_00497d30);
    }
    iVar5 = 0;
  }
  else {
    iVar6 = osMutexAcquire(*DAT_00497938,0xffffffff);
    piVar3 = DAT_0049795c;
    iVar5 = DAT_00497958;
    if (iVar6 == 0) {
      for (iVar6 = 0; iVar6 < 10; iVar6 = iVar6 + 1) {
        if (*(char *)(iVar6 * 0x304 + DAT_00497958 + 0x2fc) == '\0') {
          FUN_0043c0e4(DAT_00497958 + iVar6 * 0x304,0x304,0);
          *(undefined1 *)(iVar6 * 0x304 + iVar5 + 0x2fc) = 1;
          if (*DAT_0049795c == 0) {
            *DAT_0049795c = iVar6 * 0x304 + iVar5;
          }
          else {
            for (iVar7 = *DAT_0049795c; *(int *)(iVar7 + 0x300) != 0;
                iVar7 = *(int *)(iVar7 + 0x300)) {
            }
            *(int *)(iVar7 + 0x300) = iVar6 * 0x304 + iVar5;
          }
          pcVar4 = DAT_00497d24;
          *DAT_00497d24 = *DAT_00497d24 + '\x01';
          cVar1 = *pcVar4;
          iVar5 = iVar6 * 0x304 + iVar5;
          osMutexRelease(*piVar2);
          CB_ANCC_NotifyMsgCount(0,cVar1);
          goto LAB_00497822;
        }
      }
      if (*DAT_0049795c == 0) {
        osMutexRelease(*piVar2);
        iVar5 = 0;
      }
      else {
        iVar5 = *DAT_0049795c;
        *DAT_0049795c = *(int *)(*DAT_0049795c + 0x300);
        FUN_0043c0e4(iVar5,0x304,0);
        *(undefined1 *)(iVar5 + 0x2fc) = 1;
        *(undefined4 *)(iVar5 + 0x300) = 0;
        for (iVar6 = *piVar3; *(int *)(iVar6 + 0x300) != 0; iVar6 = *(int *)(iVar6 + 0x300)) {
        }
        *(int *)(iVar6 + 0x300) = iVar5;
        osMutexRelease(*piVar2);
      }
    }
    else {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        param_3 = 0xf0;
        FUN_0043d574(1,DAT_00497948,DAT_00497944,DAT_00497d54,0xf0,DAT_00497d58);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00497d5c);
      }
      iVar5 = 0;
    }
  }
LAB_00497822:
  return CONCAT44(param_3,iVar5);
}

