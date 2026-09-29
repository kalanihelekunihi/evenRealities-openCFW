
void ui_onboarding_main_sub_004A9118(void)

{
  int *piVar1;
  int iVar2;
  
  *DAT_004a9190 = 0;
  *DAT_004a99cc = 1;
  ui_onboarding_main_sub_004A9198(*DAT_004a99c8);
  piVar1 = DAT_004a9194;
  if ((*DAT_004a9194 != 0) && (iVar2 = ui_common_api_fn_00509dfa(*DAT_004a9194), iVar2 == 0)) {
    ui_common_api_fn_00509f52(*piVar1);
  }
  return;
}

