
undefined8
ui_onboarding_main_sub_004A90CC(undefined4 param_1,int param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uStack_14;
  int iStack_10;
  
  uStack_14 = param_3;
  iStack_10 = param_4;
  FUN_0043f506(param_1,param_2,param_3,param_4,param_2);
  ui_common_api_fn_00509f7a(&iStack_10,&uStack_14);
  FUN_0043f09a(*DAT_004a91bc,(iStack_10 - param_2) + 0x160,uStack_14);
  uVar1 = FUN_0044dca2(param_1);
  uVar2 = 0;
  FUN_0043f6d6(param_1,uVar1,3,0);
  return CONCAT44(uStack_14,uVar2);
}

