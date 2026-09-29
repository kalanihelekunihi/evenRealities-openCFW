
undefined8
ui_onboarding_main_sub_004A9E48
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_004aa164;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_004aa164 != 0) {
    if (*DAT_004aaa48 == 0) {
      FUN_0050a9c2();
    }
    else if (*DAT_004aaa48 == 1) {
      ui_onboarding_stock_sub_0050DAB8();
    }
    FUN_0043f506(*piVar1,0x160);
    uVar2 = FUN_0044dca2(*piVar1);
    local_10 = 0;
    FUN_0043f6d6(*piVar1,uVar2,3,0);
    ui_common_api_fn_00509f7a(&local_c,&local_10);
    FUN_0043f09a(*DAT_004aa150,local_c,local_10);
    FUN_0043ded4(*piVar1,1);
    *DAT_004aaa9c = 0;
    *DAT_004aa03c = 0;
    piVar1 = DAT_004aa210;
    if ((*DAT_004aa210 != 0) && (iVar3 = ui_common_api_fn_00509dfa(*DAT_004aa210), iVar3 == 0)) {
      ui_common_api_fn_00509f52(*piVar1);
    }
  }
  return CONCAT44(local_c,local_10);
}

