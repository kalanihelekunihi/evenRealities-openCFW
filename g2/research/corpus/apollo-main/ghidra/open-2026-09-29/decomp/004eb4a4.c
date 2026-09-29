
undefined4 FUN_004eb4a4(char *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int *piVar2;
  uint *puVar3;
  int *piVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  
  piVar2 = DAT_004eb784;
  if (*DAT_004eb784 == 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004ebf1c,DAT_004ebdf8,DAT_004ebf34,0x3ab,DAT_004ebf30);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004ebf38);
    }
    return 0;
  }
  if ((param_1 == (char *)0x0) || (param_2 == 0)) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ebf1c,DAT_004ebdf8,DAT_004ebf34,0x3b0,DAT_004ebf3c);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ebf40,DAT_004ebf40);
    }
    return 0xffffffff;
  }
  cVar1 = *param_1;
  if (cVar1 != '\0') {
    if (cVar1 == '\x01') {
      FUN_004e8970(param_1 + 1,param_2 + -1,param_3,param_4,param_1,param_2,param_3,param_4);
      return 0;
    }
    if (cVar1 != '\x04') {
      return 0;
    }
    FUN_004ebf5c(param_1 + 1,param_2 + -1);
    return 0;
  }
  cVar1 = param_1[1];
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004ebf1c,DAT_004ebdf8,DAT_004ebf34,0x3ba,DAT_004ebf44,cVar1);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004ebf48,DAT_004ebf48,cVar1);
  }
  piVar4 = DAT_004ec218;
  if (*(char *)(DAT_004eb740 + 0x124) != '\0') {
    if (*DAT_004eb780 != 0) {
      ui_common_api_fn_00509ca2(*DAT_004eb780,param_1 + 1,5);
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004ebf1c,DAT_004ebdf8,DAT_004ebf34,0x3c0,DAT_004ebf4c,cVar1);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004ebf50,DAT_004ebf50,cVar1);
      }
    }
    return 0;
  }
  if (cVar1 != '\n') {
    if (cVar1 == 'D') {
      FUN_004ead10(1);
      return 0;
    }
    if (cVar1 == 'E') {
      FUN_004ead10(0xffffffff);
      return 0;
    }
    if (cVar1 == 'G') {
      if (*piVar2 != 1) {
        return 0;
      }
      if (*DAT_004eb780 == 0) {
        return 0;
      }
      if (*DAT_004ec218 == 0) {
        return 0;
      }
      FUN_0044d878(*DAT_004ec218);
      FUN_004eb7b8(*piVar4);
      return 0;
    }
    if (cVar1 != 'H') {
      return 0;
    }
  }
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    uVar6 = FUN_004ebf20();
    FUN_0043d574(3,DAT_004ebf1c,DAT_004ebdf8,DAT_004ebf34,0x3cf,DAT_004ebf54,uVar6);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    uVar6 = FUN_004ebf20();
    compress_log_output(0xc400000,DAT_004ebf58,DAT_004ebf58,uVar6);
  }
  piVar2 = DAT_004ec218;
  iVar5 = FUN_0044ddea(*DAT_004ec218);
  while (iVar5 = iVar5 + -1, -1 < iVar5) {
    iVar7 = FUN_0044dce2(*piVar2,iVar5);
    if (iVar7 != 0) {
      FUN_0044d7b8();
    }
  }
  FUN_004ed440();
  puVar3 = DAT_004eb7a4;
  FUN_005000cc(*DAT_004eb7a4,2);
  FUN_004e92f4();
  if (*puVar3 < 6) {
    if (*(int *)(DAT_004eb7a8 + *puVar3 * 8 + 4) != 0) {
      FUN_0044d878(*(undefined4 *)(DAT_004eb7a8 + *puVar3 * 8 + 4));
    }
    FUN_004ec2dc(*puVar3);
  }
  return 0;
}

