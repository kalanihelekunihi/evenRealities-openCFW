
undefined4 FUN_0055daae(uint *param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055e1f8)) {
    uVar1 = 2;
  }
  else {
    *param_1 = *param_1 & 0xfeffffff;
    *param_1 = *param_1 & 0xff000000;
    param_1[1] = 0;
  }
  return uVar1;
}

