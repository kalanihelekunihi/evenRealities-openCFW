
void ui_onboarding_main_sub_004A8A82(int param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int local_70;
  undefined4 local_6c;
  undefined4 local_60;
  undefined4 local_50;
  undefined4 local_40;
  
  piVar2 = DAT_004a9390;
  piVar1 = DAT_004a91c4;
  if (*DAT_004a91c4 != 0) {
    iVar3 = FUN_0043fce0(*DAT_004a91c4);
    *piVar2 = iVar3;
    if ((param_1 == 1) && (*DAT_004a8e60 + -1 <= *DAT_004a91c0)) {
      iVar3 = *piVar2 - *DAT_004a8e64;
    }
    else {
      if (param_1 != -1) {
        return;
      }
      if (0 < *DAT_004a91c0) {
        return;
      }
      iVar3 = *DAT_004a8e64 + *piVar2;
    }
    FUN_004503d6(&local_70);
    local_70 = *piVar1;
    FUN_004506ce(&local_70,*piVar2,iVar3);
    local_40 = *DAT_004a9150;
    local_6c = DAT_004a9394;
    local_50 = DAT_004a91e8;
    local_60 = DAT_004a939c;
    *DAT_004a9190 = 1;
    FUN_00450408(&local_70);
  }
  return;
}

