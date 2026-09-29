
undefined4 FUN_004d0d80(char *param_1,short param_2)

{
  short sVar1;
  uint *puVar2;
  char *pcVar3;
  char *pcVar4;
  int *piVar5;
  undefined4 uVar6;
  short sVar7;
  int iVar8;
  
  uVar6 = DAT_004d159c;
  pcVar3 = DAT_004d1560;
  if (*param_1 != -0x56) {
    return 10;
  }
  if ((param_1[3] == '\0') && (param_2 == 8)) {
    return 0;
  }
  if (((*DAT_004d1560 != '\0') && (1 < (byte)param_1[5])) && (param_1[2] == *DAT_004d1564)) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d1554,DAT_004d1550,DAT_004d156c,0x61,DAT_004d1568,param_1[5],param_1[2])
      ;
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_004d1570,DAT_004d1570,param_1[5],param_1[2]);
    }
    return 0;
  }
  if (param_1[6] == -0x3c) {
    *DAT_004d1574 = 1;
    puVar2 = DAT_004d155c;
    *DAT_004d155c = (byte)param_1[3] - 2;
    sVar1 = *(short *)(param_1 + *puVar2 + 8);
    sVar7 = FUN_0049acd4(param_1 + 8,*puVar2,0);
    if (sVar7 == sVar1) {
      if ((((byte)param_1[7] & 0x3f) >> 5 == 0) && (*DAT_004d1578 != 0)) {
        (*(code *)*DAT_004d1578)(param_1[6],param_1 + 8,*puVar2 & 0xffff);
      }
    }
    else {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004d1554,DAT_004d1550,DAT_004d156c,0x73,DAT_004d157c);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004d1580,DAT_004d1580);
      }
      *pcVar3 = '\x01';
      *DAT_004d1564 = param_1[2];
      semantic_EfsNotifyStatus2(param_1[6]);
    }
    if ((param_1[6] == -0x3c) && (param_1[8] == '\x01')) {
      *puVar2 = 0;
      piVar5 = DAT_004d1584;
      *DAT_004d1584 = 0;
      *pcVar3 = '\0';
      pcVar4 = DAT_004d1564;
      *DAT_004d1564 = '\0';
      *piVar5 = *DAT_004d1588;
      if (*piVar5 == 0) {
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004d1554,DAT_004d1550,DAT_004d156c,0x85,DAT_004d158c);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004d1590,DAT_004d1590);
        }
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004d1554,DAT_004d1550,DAT_004d156c,0x86,DAT_004d1594);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004d1598,DAT_004d1598);
        }
        *pcVar3 = '\x01';
        *pcVar4 = param_1[2];
        semantic_EfsNotifyStatus5(param_1[6]);
        return 4;
      }
      FUN_0043c0e4(*piVar5,0x1020,0);
    }
  }
  else if (param_1[6] == -0x3b) {
    fw_event_loop_remove_delayed(DAT_004d159c);
    *pcVar3 = '\0';
    piVar5 = DAT_004d1584;
    puVar2 = DAT_004d155c;
    if ((*DAT_004d1584 == 0) && ((byte)param_1[5] < (byte)param_1[4])) {
      return 4;
    }
    if (0x1020 < *DAT_004d155c + (uint)(byte)param_1[3]) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004d1554,DAT_004d1550,DAT_004d156c,0xa0,DAT_004d15a0,*puVar2,param_1[3],
                     param_1[5],param_1[4]);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x5000000,DAT_004d15a4,DAT_004d15a4,*puVar2,param_1[3],param_1[5],
                            param_1[4]);
      }
      *puVar2 = 0;
      *pcVar3 = '\x01';
      *DAT_004d1564 = param_1[2];
      semantic_EfsNotifyStatus2(param_1[6]);
      return 4;
    }
    FUN_00439be4(*DAT_004d1584 + *DAT_004d155c,param_1 + 8,param_1[3]);
    *puVar2 = *puVar2 + (uint)(byte)param_1[3];
    if ((byte)param_1[5] < (byte)param_1[4]) {
      fw_event_loop_push_delayed(uVar6,0,0x5dc);
      return 0;
    }
    *puVar2 = *puVar2 - 2;
    sVar1 = *(short *)(*piVar5 + *puVar2);
    sVar7 = FUN_0049acd4(*piVar5,*puVar2,0);
    if (sVar7 != sVar1) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004d1554,DAT_004d1550,DAT_004d156c,0xbf,DAT_004d15b0,*puVar2);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004d15b4,DAT_004d15b4,*puVar2);
      }
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004d1554,DAT_004d1550,DAT_004d156c,0xc0,DAT_004d15b8,sVar1,sVar7);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004d15bc,DAT_004d15bc,sVar1,sVar7);
      }
      if (*piVar5 != *DAT_004d1588) {
        file_heap_free(*piVar5);
      }
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004d1554,DAT_004d1550,DAT_004d156c,0xc5,DAT_004d15c0);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004d15c4,DAT_004d15c4);
      }
      *puVar2 = 0;
      *pcVar3 = '\x01';
      *DAT_004d1564 = param_1[2];
      semantic_EfsNotifyStatus2(param_1[6]);
      return 1;
    }
    if (*DAT_004d1578 != 0) {
      (*(code *)*DAT_004d1578)(param_1[6],*piVar5,*puVar2 & 0xffff);
    }
    if (*piVar5 != *DAT_004d1588) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004d1554,DAT_004d1550,DAT_004d156c,0xce,DAT_004d15a8,*piVar5);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004d15ac,DAT_004d15ac,*piVar5);
      }
      file_heap_free(*piVar5);
    }
    *piVar5 = 0;
    *puVar2 = 0;
  }
  else if (param_1[6] == -0x3a) {
    *DAT_004d1574 = 1;
    puVar2 = DAT_004d155c;
    *DAT_004d155c = (byte)param_1[3] - 2;
    sVar1 = *(short *)(param_1 + *puVar2 + 8);
    sVar7 = FUN_0049acd4(param_1 + 8,*puVar2,0);
    if (sVar7 == sVar1) {
      if ((((byte)param_1[7] & 0x3f) >> 5 == 0) && (*DAT_004d1578 != 0)) {
        (*(code *)*DAT_004d1578)(param_1[6],param_1 + 8,*puVar2 & 0xffff);
      }
    }
    else {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004d1554,DAT_004d1550,DAT_004d156c,0xe1,DAT_004d157c);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004d1580,DAT_004d1580);
      }
      *pcVar3 = '\x01';
      *DAT_004d1564 = param_1[2];
      semantic_EfsNotifyStatus2(param_1[6]);
    }
  }
  return 0;
}

