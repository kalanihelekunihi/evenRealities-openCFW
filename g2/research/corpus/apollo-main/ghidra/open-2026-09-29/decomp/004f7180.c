
void FUN_004f7180(char param_1)

{
  bool bVar1;
  undefined4 *puVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int local_88;
  int local_84;
  int local_80;
  undefined4 local_7c;
  undefined4 local_70;
  undefined4 local_50;
  
  piVar3 = DAT_004f7ae0;
  if ((*DAT_004f7ae0 != 0) && (iVar5 = FUN_0043e0e0(*DAT_004f7ae0,1), iVar5 != 0)) {
    uVar6 = osKernelGetTickCount();
    puVar2 = DAT_004f7c04;
    *DAT_004f7c04 = uVar6;
    puVar2[1] = 0;
    *DAT_004f7c08 = 1;
    FUN_0043dfa4(*piVar3,1);
    FUN_00441488(*piVar3,0xff,0);
    FUN_004f82d0();
    puVar2 = DAT_004f747c;
    iVar5 = FUN_0043fdda(*DAT_004f747c);
    iVar7 = FUN_0043fdda(*piVar3);
    iVar8 = FUN_0044e498(*puVar2);
    piVar4 = DAT_004f7c0c;
    *DAT_004f7c0c = iVar8;
    if (param_1 == '\0') {
      iVar5 = 0;
      if ((*DAT_004f7c90 != 0) && (*DAT_004f7c88 != 0)) {
        iVar5 = FUN_0043fce0(*DAT_004f7c88);
      }
      iVar8 = iVar7 + 4 + iVar5;
      FUN_0043f142(*piVar3,0);
      FUN_004f7f18(iVar8);
      *piVar4 = iVar8;
      FUN_0044ea04(*puVar2,iVar8,0);
      FUN_004f6f9c(*puVar2,0,100);
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f758c,DAT_004f7588,DAT_004f7c9c,0x88e,DAT_004f7cac,iVar5,iVar8);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004f7fa4,DAT_004f7fa4,iVar5,iVar8);
      }
    }
    else {
      local_84 = 0;
      local_88 = 0;
      if (*DAT_004f7c90 != 0) {
        FUN_004f6fc4(*DAT_004f7c90 - 1,0,&local_84,0,&local_88);
      }
      iVar9 = local_88 + local_84 + 4;
      if ((iVar5 < iVar7 + (iVar9 - iVar8)) || (iVar9 - iVar8 < 0)) {
        bVar1 = false;
      }
      else {
        bVar1 = true;
      }
      if (bVar1) {
        FUN_0043f142(*piVar3,iVar5);
        FUN_004503d6(&local_80);
        local_80 = *piVar3;
        FUN_004506ce(&local_80,iVar5,iVar5 - iVar7);
        local_50 = 100;
        local_7c = DAT_004f7c94;
        local_70 = DAT_004f7790;
        FUN_00450408(&local_80);
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004f758c,DAT_004f7588,DAT_004f7c9c,0x84b,DAT_004f7c98,iVar5,
                       iVar5 - iVar7);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_004f7ca0,DAT_004f7ca0,iVar5,iVar5 - iVar7);
        }
      }
      else {
        FUN_0043f142(*piVar3,iVar9);
        iVar5 = (iVar7 + iVar9) - iVar5;
        FUN_004f6f9c(*puVar2,iVar5,100);
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004f758c,DAT_004f7588,DAT_004f7c9c,0x856,DAT_004f7ca4,iVar9,iVar5);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_004f7ca8,DAT_004f7ca8,iVar9,iVar5);
        }
      }
    }
  }
  return;
}

