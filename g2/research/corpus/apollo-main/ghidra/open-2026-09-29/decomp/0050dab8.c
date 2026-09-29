
undefined4 ui_onboarding_stock_sub_0050DAB8(void)

{
  int *piVar1;
  uint *puVar2;
  int iVar3;
  int iVar4;
  undefined4 in_r3;
  
  piVar1 = DAT_0050dc68;
  if (*DAT_0050dc68 != 0) {
    ui_onboarding_stock_sub_0050E534();
    iVar3 = FUN_0044ddea(*piVar1);
    while (iVar3 = iVar3 + -1, -1 < iVar3) {
      iVar4 = FUN_0044dce2(*piVar1,iVar3);
      if (iVar4 != 0) {
        FUN_0044d7b8();
      }
    }
    ui_onboarding_stock_sub_0050E728();
    ui_onboarding_stock_sub_0050E870();
    puVar2 = DAT_0050dddc;
    if (*DAT_0050dddc < 6) {
      if (*(int *)(DAT_0050dc6c + *DAT_0050dddc * 8 + 4) != 0) {
        FUN_0044d878(*(undefined4 *)(DAT_0050dc6c + *DAT_0050dddc * 8 + 4));
      }
      ui_onboarding_stock_sub_0050DCBC(*puVar2);
    }
  }
  return in_r3;
}

