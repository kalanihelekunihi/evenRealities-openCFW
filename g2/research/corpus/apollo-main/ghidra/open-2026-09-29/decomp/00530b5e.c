
void L2cRegister(short param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  
  puVar1 = DAT_00530b90;
  if (param_1 == 4) {
    *DAT_00530b90 = param_2;
    puVar1[3] = param_3;
  }
  else {
    DAT_00530b90[1] = param_2;
    puVar1[4] = param_3;
  }
  return;
}

