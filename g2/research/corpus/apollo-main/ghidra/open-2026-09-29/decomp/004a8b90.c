
void ui_onboarding_main_sub_004A8B90(int param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  
  piVar2 = DAT_004a91c4;
  if ((*DAT_004a91c4 != 0) && (*DAT_004a9190 == 0)) {
    iVar3 = FUN_0044e498(*DAT_004a91c4);
    piVar1 = DAT_004a91c0;
    iVar4 = iVar3;
    if ((param_1 == 1) && (iVar4 = *DAT_004a91c0, iVar4 < *DAT_004a8e60 + -1)) {
      *DAT_004a91c0 = *DAT_004a91c0 + 1;
      ui_onboarding_main_sub_004A8B30(*piVar2,iVar3 + 0x130,*DAT_004a914c);
      ui_onboarding_main_sub_004A859E(*piVar1,0);
      return;
    }
    if ((param_1 == -1) && (iVar4 = *DAT_004a91c0, 0 < iVar4)) {
      *DAT_004a91c0 = *DAT_004a91c0 + -1;
      ui_onboarding_main_sub_004A8B30(*piVar2,iVar3 + -0x130,*DAT_004a914c);
      ui_onboarding_main_sub_004A859E(*piVar1,0);
      return;
    }
    ui_onboarding_main_sub_004A8A82(param_1,iVar3,iVar4);
  }
  return;
}

