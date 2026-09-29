
void system_close_update_selection(void)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  piVar2 = DAT_0046ae98;
  piVar1 = DAT_0046ae94;
  if (*DAT_0046ae94 != 0) {
    iVar6 = 0;
    if (*DAT_0046ae98 == 0) {
      iVar6 = *DAT_0046acd4;
    }
    else if ((*DAT_0046b00c == 2) && (*DAT_0046ae98 == 1)) {
      iVar6 = *DAT_0046acd8;
    }
    else if ((*DAT_0046b00c == 3) && (*DAT_0046ae98 == 1)) {
      iVar6 = *DAT_0046acd8;
    }
    else if ((*DAT_0046b00c == 3) && (*DAT_0046ae98 == 2)) {
      iVar6 = *DAT_0046b010;
    }
    iVar7 = 0;
    iVar8 = 0;
    if (iVar6 != 0) {
      iVar7 = FUN_0043fc70(iVar6);
      iVar8 = FUN_0043fce0(iVar6);
      iVar6 = FUN_0043fdda(iVar6);
      iVar3 = FUN_0043fd9e(*piVar1);
      iVar4 = FUN_0043fdda(*piVar1);
      iVar7 = (iVar7 - iVar3) + -8;
      iVar8 = (iVar6 - iVar4) / 2 + iVar8;
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0046a834,DAT_0046a830,DAT_0046b018,0x1c3,DAT_0046b014,*piVar2,iVar7,iVar8);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_0046b01c,DAT_0046b01c,*piVar2,iVar7,iVar8);
    }
    FUN_0043f09a(*piVar1,iVar7,iVar8);
    piVar1 = DAT_0046acd4;
    if (*DAT_0046acd4 != 0) {
      if (*piVar2 == 0) {
        uVar5 = FUN_0044104c(0xffffff);
      }
      else {
        uVar5 = FUN_0044104c(DAT_0046b020);
      }
      FUN_0044140e(*piVar1,uVar5,0);
    }
    piVar1 = DAT_0046acd8;
    if (*DAT_0046acd8 != 0) {
      if (*piVar2 == 1) {
        uVar5 = FUN_0044104c(0xffffff);
      }
      else {
        uVar5 = FUN_0044104c(DAT_0046b020);
      }
      FUN_0044140e(*piVar1,uVar5,0);
    }
    piVar1 = DAT_0046b010;
    if ((*DAT_0046b010 != 0) && (*DAT_0046b00c == 3)) {
      if (*piVar2 == 2) {
        uVar5 = FUN_0044104c(0xffffff);
      }
      else {
        uVar5 = FUN_0044104c(DAT_0046b020);
      }
      FUN_0044140e(*piVar1,uVar5,0);
    }
  }
  return;
}

