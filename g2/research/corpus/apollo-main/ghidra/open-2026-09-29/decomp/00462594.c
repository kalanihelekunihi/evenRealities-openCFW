
void FUN_00462594(int param_1)

{
  char *pcVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  
  piVar2 = DAT_00462f28;
  pcVar1 = DAT_00462ea4;
  if (*DAT_00462e94 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0046289c,DAT_00462898,DAT_00462e9c,0x447,DAT_00462e98);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00462ea0,DAT_00462ea0);
    }
  }
  else if (*DAT_00462ea4 == '\0') {
    if ((param_1 < 0) || (*DAT_00462f28 <= param_1)) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0046289c,DAT_00462898,DAT_00462e9c,0x453,DAT_00462f2c,param_1,
                     *DAT_00462f28 + -1);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8800000,DAT_00462f30,DAT_00462f30,param_1,*DAT_00462f28 + -1);
      }
    }
    else if (param_1 == *DAT_00462f34) {
      iVar5 = FUN_0043d0ce();
      iVar4 = DAT_00463014;
      if (iVar5 << 0x1e < 0) {
        uVar6 = FUN_00460084(param_1 * 0x34 + DAT_00463014 + 4);
        uVar6 = FUN_0045fffe(iVar4 + param_1 * 0x34 + 4,uVar6);
        FUN_0043d574(4,DAT_0046289c,DAT_00462898,DAT_00462e9c,0x459,DAT_00463018,param_1,uVar6);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        iVar4 = DAT_00463014;
        uVar6 = FUN_00460084(param_1 * 0x34 + DAT_00463014 + 4);
        uVar6 = FUN_0045fffe(iVar4 + param_1 * 0x34 + 4,uVar6);
        compress_log_output(0x10800000,DAT_0046301c,DAT_0046301c,param_1,uVar6);
      }
    }
    else {
      iVar4 = *DAT_00462f34;
      *DAT_00462f34 = param_1;
      piVar3 = DAT_00463020;
      if (param_1 < 2) {
        *DAT_00463020 = 0;
      }
      else if (param_1 < *piVar2 + -2) {
        *DAT_00463020 = param_1 + -2;
      }
      else {
        *DAT_00463020 = *piVar2 + -5;
        if (*piVar3 < 0) {
          *piVar3 = 0;
        }
      }
      *pcVar1 = '\x01';
      uVar6 = FUN_00460d6c(param_1);
      iVar7 = FUN_0043d0ce();
      iVar5 = DAT_00463014;
      if (iVar7 << 0x1e < 0) {
        uVar8 = FUN_00460084(param_1 * 0x34 + DAT_00463014 + 4);
        uVar8 = FUN_0045fffe(param_1 * 0x34 + iVar5 + 4,uVar8);
        uVar9 = FUN_00460084(iVar4 * 0x34 + iVar5 + 4);
        uVar9 = FUN_0045fffe(iVar5 + iVar4 * 0x34 + 4,uVar9);
        FUN_0043d574(4,DAT_0046289c,DAT_00462898,DAT_00462e9c,0x471,DAT_00463024,iVar4,uVar9,param_1
                     ,uVar8,*DAT_00463020,uVar6);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        iVar5 = DAT_00463014;
        uVar8 = FUN_00460084(param_1 * 0x34 + DAT_00463014 + 4);
        uVar8 = FUN_0045fffe(param_1 * 0x34 + iVar5 + 4,uVar8);
        uVar9 = FUN_00460084(iVar4 * 0x34 + iVar5 + 4);
        uVar9 = FUN_0045fffe(iVar5 + iVar4 * 0x34 + 4,uVar9);
        compress_log_output(0x11800000,DAT_00463028,DAT_00463028,iVar4,uVar9,param_1,uVar8,
                            *DAT_00463020,uVar6);
      }
      FUN_00460fc6(*DAT_004631ac,uVar6,200);
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0046289c,DAT_00462898,DAT_00462e9c,0x44d,DAT_00462f20);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00462f24);
    }
  }
  return;
}

