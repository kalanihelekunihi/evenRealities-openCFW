
void ui_onboarding_main_sub_004A87D8(void)

{
  int *piVar1;
  int iVar2;
  undefined1 auStack_20 [8];
  undefined1 auStack_18 [12];
  
  *DAT_004a9190 = 0;
  piVar1 = DAT_004a9194;
  if ((*DAT_004a9194 != 0) && (iVar2 = ui_common_api_fn_00509dfa(*DAT_004a9194), iVar2 == 0)) {
    FUN_0043c0e4(auStack_18,10,0);
    ui_common_api_fn_00509e14(*piVar1,auStack_18,7);
    iVar2 = ui_onboarding_main_sub_004A979C(auStack_18,0,auStack_20);
    if (iVar2 == 0) {
      ui_onboarding_main_sub_004A97EA(auStack_20);
    }
  }
  return;
}

