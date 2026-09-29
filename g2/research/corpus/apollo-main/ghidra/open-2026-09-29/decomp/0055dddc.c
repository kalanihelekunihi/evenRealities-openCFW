
undefined4 FUN_0055dddc(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055e1f8)) {
    uVar1 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    uVar1 = 0;
  }
  else {
    *DAT_0055e1fc = *DAT_0055e1fc | 1;
    *param_1 = *param_1 | 0x2000000;
    uVar1 = 0;
  }
  return uVar1;
}

