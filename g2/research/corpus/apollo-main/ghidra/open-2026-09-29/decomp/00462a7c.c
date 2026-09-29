
void FUN_00462a7c(int param_1)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  
  piVar2 = DAT_00462f34;
  piVar1 = DAT_00462f28;
  if (*DAT_00462e94 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004631bc,DAT_004631b8,DAT_004631d4,0x4cc,DAT_00462e98);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00462ea0,DAT_00462ea0);
    }
  }
  else if (*DAT_00462f28 < param_1) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004631bc,DAT_004631b8,DAT_004631d4,0x4d1,DAT_004631d8,param_1);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004631dc,DAT_004631dc,param_1);
    }
  }
  else if (param_1 == *DAT_00462f34) {
    iVar5 = FUN_0043d0ce();
    iVar4 = DAT_00463014;
    if (iVar5 << 0x1e < 0) {
      uVar6 = FUN_00460084(param_1 * 0x34 + DAT_00463014 + 4);
      uVar6 = FUN_0045fffe(iVar4 + param_1 * 0x34 + 4,uVar6);
      FUN_0043d574(4,DAT_004631bc,DAT_004631b8,DAT_004631d4,0x4d9,DAT_004631e0,uVar6,param_1);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      iVar4 = DAT_00463014;
      uVar6 = FUN_00460084(param_1 * 0x34 + DAT_00463014 + 4);
      uVar6 = FUN_0045fffe(iVar4 + param_1 * 0x34 + 4,uVar6);
      compress_log_output(0x10800000,DAT_004631e4,DAT_004631e4,uVar6,param_1);
    }
    FUN_00462db6();
    FUN_00462db4();
  }
  else {
    iVar4 = *DAT_00462f34;
    *DAT_00462f34 = param_1;
    piVar3 = DAT_00463020;
    if (param_1 < 2) {
      *DAT_00463020 = 0;
    }
    else if (param_1 < *piVar1 + -2) {
      *DAT_00463020 = param_1 + -2;
    }
    else {
      *DAT_00463020 = *piVar1 + -5;
      if (*piVar3 < 0) {
        *piVar3 = 0;
      }
    }
    uVar6 = FUN_00460d6c(param_1);
    iVar7 = FUN_0043d0ce();
    iVar5 = DAT_00463014;
    if (iVar7 << 0x1e < 0) {
      uVar8 = FUN_00460084(param_1 * 0x34 + DAT_00463014 + 4);
      uVar8 = FUN_0045fffe(param_1 * 0x34 + iVar5 + 4,uVar8);
      uVar9 = FUN_00460084(iVar4 * 0x34 + iVar5 + 4);
      uVar9 = FUN_0045fffe(iVar5 + iVar4 * 0x34 + 4,uVar9);
      FUN_0043d574(4,DAT_004631bc,DAT_004631b8,DAT_004631d4,0x4f3,DAT_004631e8,iVar4,uVar9,param_1,
                   uVar8,*DAT_00463020,uVar6);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      iVar5 = DAT_00463014;
      uVar8 = FUN_00460084(param_1 * 0x34 + DAT_00463014 + 4);
      uVar8 = FUN_0045fffe(param_1 * 0x34 + iVar5 + 4,uVar8);
      uVar9 = FUN_00460084(iVar4 * 0x34 + iVar5 + 4);
      uVar9 = FUN_0045fffe(iVar5 + iVar4 * 0x34 + 4,uVar9);
      compress_log_output(0x11800000,DAT_004631ec,DAT_004631ec,iVar4,uVar9,param_1,uVar8,
                          *DAT_00463020,uVar6);
    }
    FUN_0044ea04(*DAT_004631ac,uVar6,0);
    FUN_00462db6();
    FUN_00462db4();
    iVar5 = FUN_0043d0ce();
    iVar4 = DAT_00463014;
    if (iVar5 << 0x1e < 0) {
      uVar6 = FUN_00460084(*piVar2 * 0x34 + DAT_00463014 + 4);
      uVar6 = FUN_0045fffe(iVar4 + *piVar2 * 0x34 + 4,uVar6);
      FUN_0043d574(4,DAT_004631bc,DAT_004631b8,DAT_004631d4,0x4fe,DAT_004631f0,uVar6,*piVar2);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      iVar4 = DAT_00463014;
      uVar6 = FUN_00460084(*piVar2 * 0x34 + DAT_00463014 + 4);
      uVar6 = FUN_0045fffe(iVar4 + *piVar2 * 0x34 + 4,uVar6);
      compress_log_output(0x10800000,DAT_004631f4,DAT_004631f4,uVar6,*piVar2);
    }
  }
  return;
}

