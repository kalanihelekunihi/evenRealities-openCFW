
undefined4 ui_onboarding_main_sub_004AAAA8(void)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined4 in_r3;
  
  if (*DAT_004ab6cc == 1) {
    ui_onboarding_main_sub_004A9E48();
  }
  piVar2 = DAT_004aae30;
  if (*DAT_004aae30 != 0) {
    FUN_0044ea04(*DAT_004aae30,0,0);
    *DAT_004ab07c = 0;
    ui_onboarding_main_sub_004A859E(0,0);
  }
  FUN_0043ded4(*DAT_004aab78,1);
  FUN_0043ded4(*DAT_004aab84,1);
  FUN_0050fe0e();
  puVar1 = DAT_004aae2c;
  FUN_0043dfa4(*DAT_004aae2c,1);
  FUN_00441488(*puVar1,0xff,0);
  ui_onboarding_main_sub_004A859E(*DAT_004ab07c,0);
  FUN_0043dfa4(*piVar2,1);
  FUN_00441488(*piVar2,0xff,0);
  FUN_0043ded4(*DAT_004aae34,1);
  FUN_0043ded4(*DAT_004aab88,1);
  FUN_0043ded4(*DAT_004ab000,1);
  return in_r3;
}

