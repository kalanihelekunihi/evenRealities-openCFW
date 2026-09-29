
void ui_onboarding_main_sub_004A8968(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
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
      local_70 = 0x218;
      FUN_0043d574(2,DAT_004a91dc,DAT_004a91d8,DAT_004a91f0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004a91e0,DAT_004a91e0);
    }
  }
  else {
    uVar3 = FUN_0043fc70(*DAT_004a91cc);
    FUN_0043f66c(*piVar1);
    iVar2 = FUN_0043fd9e(*piVar1);
    FUN_004503d6(&local_70);
    local_70 = *piVar1;
    FUN_004506ce(&local_70,uVar3,-iVar2);
    local_40 = 0xfa;
    local_6c = DAT_004a91e4;
    local_50 = DAT_004a9388;
    local_60 = DAT_004a938c;
    *DAT_004a9190 = 1;
    FUN_00450408(&local_70);
  }
  return;
}

