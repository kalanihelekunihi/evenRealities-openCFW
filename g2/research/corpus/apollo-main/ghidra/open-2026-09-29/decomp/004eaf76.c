
void FUN_004eaf76(void)

{
  int *piVar1;
  int *piVar2;
  uint *puVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  undefined4 in_r3;
  char local_24 [12];
  undefined4 uStack_18;
  
  iVar6 = DAT_004eb740;
  *(undefined1 *)(DAT_004eb740 + 0x124) = 0;
  uStack_18 = in_r3;
  FUN_004ed37c();
  iVar5 = FUN_004ebf20();
  FUN_0050012e(iVar5 + 1);
  piVar1 = DAT_004eb780;
  if (*DAT_004eb780 == 0) {
    return;
  }
  iVar5 = ui_common_api_fn_00509dfa(*DAT_004eb780);
  piVar2 = DAT_004eb784;
  if (iVar5 != 0) {
    return;
  }
  if (*DAT_004eb784 != 1) {
    return;
  }
  FUN_0043c0e4(local_24,10,0);
  FUN_0043c0e4(local_24,10,0);
  ui_common_api_fn_00509e14(*piVar1,local_24,5);
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004eb32c,DAT_004eb328,DAT_004eb78c,0x2f3,DAT_004eb788,local_24[0]);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_004eb790,DAT_004eb790,local_24[0]);
  }
  piVar4 = DAT_004ebdd4;
  if (local_24[0] != '\n') {
    if (local_24[0] == 'D') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004eb32c,DAT_004eb328,DAT_004eb78c,0x2f8,DAT_004eb794);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004eb798,DAT_004eb798);
      }
      FUN_004ead10(1);
      return;
    }
    if (local_24[0] == 'E') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004eb32c,DAT_004eb328,DAT_004eb78c,0x2fc,DAT_004eb794);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004eb798,DAT_004eb798);
      }
      FUN_004ead10(0xffffffff);
      return;
    }
    if (local_24[0] == 'G') {
      if (*piVar2 != 1) {
        return;
      }
      if (*piVar1 == 0) {
        return;
      }
      if (*DAT_004ebdd4 == 0) {
        return;
      }
      if (*(char *)(iVar6 + 0x124) != '\0') {
        return;
      }
      FUN_0044d878(*DAT_004ebdd4);
      FUN_004eb7b8(*piVar4);
      return;
    }
    if (local_24[0] != 'H') {
      return;
    }
  }
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004eb32c,DAT_004eb328,DAT_004eb78c,0x301,DAT_004eb79c);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_004eb7a0,DAT_004eb7a0);
  }
  piVar1 = DAT_004ebdd4;
  iVar6 = FUN_0044ddea(*DAT_004ebdd4);
  while (iVar6 = iVar6 + -1, -1 < iVar6) {
    iVar5 = FUN_0044dce2(*piVar1,iVar6);
    if (iVar5 != 0) {
      FUN_0044d7b8();
    }
  }
  FUN_004ed440();
  FUN_004e92f4();
  puVar3 = DAT_004eb7a4;
  FUN_005000cc(*DAT_004eb7a4,2);
  if (*puVar3 < 6) {
    if (*(int *)(DAT_004eb7a8 + *puVar3 * 8 + 4) != 0) {
      FUN_0044d878(*(undefined4 *)(DAT_004eb7a8 + *puVar3 * 8 + 4));
    }
    FUN_004ec2dc(*puVar3);
  }
  return;
}

