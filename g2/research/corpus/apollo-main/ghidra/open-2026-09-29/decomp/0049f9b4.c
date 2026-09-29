
undefined8 _bleMasterScanStop(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  ushort *puVar3;
  undefined1 uVar4;
  int iVar5;
  
  piVar1 = DAT_004a0518;
  if (*(char *)(param_1 + 3) == '\0') {
    *(undefined1 *)(*DAT_004a0518 + 0x58) = 0;
    piVar2 = DAT_004a05e8;
    if (*(char *)(*DAT_004a05e8 + 0x15) == '\0') {
      if (*(char *)(*piVar1 + 0x59) == '\0') {
        AppAdvStart(1);
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          param_2 = 0xfb;
          param_3 = DAT_004a05ec;
          FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0520);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004a05f0,DAT_004a05f0);
        }
        *(undefined1 *)(*piVar1 + 0x59) = 0;
        central_schedule_master_connect_004a2618(0x5dc,0);
        puVar3 = DAT_004a05f4;
        *DAT_004a05f4 = *DAT_004a05f4 + 1;
        if (0x32 < *puVar3) {
          *puVar3 = 0;
          central_cancel_connect_retry_work_004a17f4();
        }
      }
    }
    else {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        param_2 = 0xf4;
        param_3 = DAT_004a051c;
        FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0520,0xf4,DAT_004a051c,param_4);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004a0524,DAT_004a0524);
      }
      *(undefined1 *)(*piVar1 + 0x59) = 0;
      uVar4 = AppConnOpen(*(undefined1 *)(*piVar2 + 8),*piVar2 + 9,*(undefined4 *)(*piVar2 + 4));
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        param_2 = 0xf8;
        param_3 = DAT_004a0528;
        FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a0520,0xf8,DAT_004a0528,uVar4);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004a052c,DAT_004a052c,uVar4);
      }
      *(undefined1 *)(*piVar2 + 0x15) = 0;
    }
  }
  return CONCAT44(param_3,param_2);
}

