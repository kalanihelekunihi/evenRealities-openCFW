
void ui_onboarding_main_sub_004A874C(void)

{
  char *pcVar1;
  int *piVar2;
  int iVar3;
  undefined4 in_r3;
  undefined2 auStack_28 [2];
  undefined1 auStack_24 [8];
  undefined1 auStack_1c [12];
  undefined4 uStack_10;
  
  *DAT_004a9190 = 0;
  pcVar1 = DAT_004a9114;
  uStack_10 = in_r3;
  if ((*DAT_004a9114 == '\x02') && (0xd < (byte)DAT_004a9114[1])) {
    *DAT_004a9114 = '\x03';
    pcVar1[1] = '\0';
    *DAT_004a9154 = 0;
    auStack_28[0] = *DAT_004a9158;
    APP_PbNotifyEncodeOnboardingConfig(0,auStack_28);
    ui_onboarding_main_sub_004A9EDC();
  }
  piVar2 = DAT_004a9194;
  if ((*DAT_004a9194 != 0) && (iVar3 = ui_common_api_fn_00509dfa(*DAT_004a9194), iVar3 == 0)) {
    FUN_0043c0e4(auStack_1c,10,0);
    ui_common_api_fn_00509e14(*piVar2,auStack_1c,7);
    iVar3 = ui_onboarding_main_sub_004A979C(auStack_1c,0,auStack_24);
    if (iVar3 == 0) {
      ui_onboarding_main_sub_004A97EA(auStack_24);
    }
  }
  return;
}

