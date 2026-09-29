
void ui_onboarding_main_sub_004A88AA(void)

{
  int *piVar1;
  int iVar2;
  int local_70;
  undefined4 local_6c;
  undefined4 local_60;
  undefined4 local_50;
  undefined4 local_40;
  
  piVar1 = DAT_004a91cc;
  if (*DAT_004a91cc == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_6c = DAT_004a91d0;
      local_70 = 0x1ec;
      FUN_0043d574(2,DAT_004a91dc,DAT_004a91d8,DAT_004a91d4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004a91e0,DAT_004a91e0);
    }
  }
  else {
    FUN_0043f66c(*DAT_004a91cc);
    iVar2 = FUN_0043fd9e(*piVar1);
    FUN_0043f0e0(*piVar1,-iVar2);
    FUN_004503d6(&local_70);
    local_70 = *piVar1;
    FUN_004506ce(&local_70,-iVar2,0);
    local_40 = 0xfa;
    local_6c = DAT_004a91e4;
    local_50 = DAT_004a91e8;
    local_60 = DAT_004a91ec;
    *DAT_004a9190 = 1;
    FUN_00450408(&local_70);
  }
  return;
}

