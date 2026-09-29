
void ui_onboarding_main_sub_004A9648(undefined4 param_1,undefined1 param_2,char param_3)

{
  undefined1 uVar1;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_60;
  undefined4 local_50;
  undefined4 local_40;
  
  *DAT_004aa03c = 1;
  FUN_004503d6(&local_70);
  local_70 = param_1;
  uVar1 = ui_onboarding_main_sub_004A8560(param_1,0);
  FUN_004506ce(&local_70,uVar1,param_2);
  local_40 = 0xfa;
  local_6c = DAT_004aa0bc;
  local_50 = DAT_004aa0c0;
  if (param_3 == '\x01') {
    local_60 = DAT_004aa0c4;
  }
  else {
    local_60 = DAT_004aa1fc;
  }
  FUN_00450408(&local_70);
  return;
}

