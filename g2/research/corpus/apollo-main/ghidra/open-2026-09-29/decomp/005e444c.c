
undefined8
terminal_ui_input_filter(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined4 unaff_r7;
  
  if (param_3 == 0x44) {
    param_3 = 0x45;
  }
  else if (param_3 == 0x45) {
    param_3 = 0x44;
  }
  if ((((param_3 == 8) || (param_3 == 10)) || (param_3 == 0x44)) ||
     (((param_3 == 0x45 || (param_3 == 0x48)) || (param_3 == 0x4a)))) {
    FUN_005e7324(param_3,param_4);
  }
  return CONCAT44(unaff_r7,1);
}

