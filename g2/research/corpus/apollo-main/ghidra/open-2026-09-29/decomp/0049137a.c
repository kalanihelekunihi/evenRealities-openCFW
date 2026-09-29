
undefined4 FUN_0049137a(void)

{
  int *piVar1;
  char *pcVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 in_r3;
  int iVar8;
  undefined1 auStack_74 [20];
  int local_60 [2];
  int local_58;
  undefined4 local_54;
  int local_50;
  undefined4 local_4c;
  undefined1 auStack_3c [24];
  undefined4 uStack_24;
  
  piVar3 = DAT_00491650;
  pcVar2 = DAT_00491630;
  uStack_24 = in_r3;
  if (*DAT_00491630 == '\0') {
    iVar5 = osMutexNew(0);
    *piVar3 = iVar5;
    if (*piVar3 == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00491628,DAT_00491624,DAT_00491668,0x80,DAT_00491670);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00491674,DAT_00491674);
      }
      uVar6 = 0xffffffff;
    }
    else {
      FUN_00439c04(auStack_3c,DAT_00491678,0x18);
      piVar1 = DAT_00491618;
      iVar5 = osMessageQueueNew(0x96,0x14,auStack_3c);
      *piVar1 = iVar5;
      if (*piVar1 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00491628,DAT_00491624,DAT_00491668,0x8f,DAT_0049167c);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00491680,DAT_00491680);
        }
        osMutexDelete(*piVar3);
        *piVar3 = 0;
        uVar6 = 0xffffffff;
      }
      else {
        iVar8 = 0;
        for (iVar5 = 0; iVar5 < 8; iVar5 = iVar5 + 1) {
          FUN_00439c04(local_60,DAT_00491684,0x24);
          FUN_0043c0e4(auStack_74,0x14,0);
          FUN_0044b728(auStack_74,0x14,DAT_00491688,iVar5);
          iVar7 = DAT_0049168c;
          FUN_0048d540(iVar5 * 0x14 + DAT_0049168c,auStack_74);
          iVar4 = DAT_00491698;
          local_60[0] = iVar7 + iVar5 * 0x14;
          local_50 = DAT_00491690 + iVar5 * 0x1000;
          local_4c = 0x1000;
          local_58 = DAT_00491694 + iVar5 * 0x70;
          local_54 = 0x70;
          uVar6 = osThreadNew(DAT_0049169c,0,local_60);
          *(undefined4 *)(iVar4 + iVar5 * 4) = uVar6;
          if (*(int *)(iVar4 + iVar5 * 4) == 0) {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              FUN_0043d574(1,DAT_00491628,DAT_00491624,DAT_00491668,0xa6,DAT_004916a0,iVar5);
            }
            iVar7 = FUN_0043d0ce();
            if (-1 < iVar7 << 0x1f) {
              iVar7 = FUN_0043d0ce();
              if (-1 < iVar7 << 0x1d) goto LAB_0049156e;
            }
            compress_log_output(0x4400000,DAT_004916a4,DAT_004916a4,iVar5);
          }
          else {
            iVar8 = iVar8 + 1;
          }
LAB_0049156e:
        }
        if (iVar8 < 1) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00491628,DAT_00491624,DAT_00491668,0xb4,DAT_004916b0);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004916b4,DAT_004916b4);
          }
          osMessageQueueDelete(*piVar1);
          *piVar1 = 0;
          osMutexDelete(*piVar3);
          *piVar3 = 0;
          uVar6 = 0xffffffff;
        }
        else {
          *pcVar2 = '\x01';
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(3,DAT_00491628,DAT_00491624,DAT_00491668,0xb0,DAT_004916a8,iVar8);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0xc400000,DAT_004916ac,DAT_004916ac,iVar8);
          }
          uVar6 = 0;
        }
      }
    }
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00491628,DAT_00491624,DAT_00491668,0x79,DAT_00491664);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0049166c,DAT_0049166c);
    }
    uVar6 = 0xffffffff;
  }
  return uVar6;
}

