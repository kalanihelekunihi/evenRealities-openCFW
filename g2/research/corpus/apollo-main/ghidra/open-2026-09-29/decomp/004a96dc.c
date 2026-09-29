
void ui_onboarding_main_sub_004A96DC(char param_1)

{
  int iVar1;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 local_38;
  
  FUN_004503d6(&local_68);
  if (*DAT_004a99cc == 1) {
    FUN_0043ded4(*DAT_004aa150,1);
    FUN_0043ded4(*DAT_004aa154,1);
    if ((*DAT_004aa158 == 1) && (iVar1 = FUN_0043e0e0(*DAT_004aa15c,1), iVar1 == 0)) {
      FUN_0043ded4(*(undefined4 *)(DAT_004aa160 + 0x30),1);
    }
    local_68 = *DAT_004aa164;
  }
  else {
    local_68 = *DAT_004aa168;
  }
  FUN_004506ce(&local_68,0xff,0);
  local_38 = 0xfa;
  local_64 = DAT_004aa0bc;
  local_48 = DAT_004aa0c0;
  if (param_1 == '\x01') {
    local_58 = DAT_004aa0c4;
  }
  else {
    local_58 = DAT_004aa1fc;
  }
  *DAT_004aa03c = 1;
  FUN_00450408(&local_68);
  return;
}

