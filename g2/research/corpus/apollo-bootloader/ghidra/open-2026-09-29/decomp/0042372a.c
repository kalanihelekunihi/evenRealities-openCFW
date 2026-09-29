
undefined4 FUN_0042372a(uint *param_1,undefined4 *param_2,char param_3)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00423830)) {
    uVar1 = 2;
  }
  else {
    if (param_3 == '\0') {
      uVar1 = *(undefined4 *)(DAT_00423764 + param_1[10] * 0x1000 + 0x3c);
    }
    else {
      uVar1 = *(undefined4 *)(DAT_00423764 + param_1[10] * 0x1000 + 0x40);
    }
    *param_2 = uVar1;
    uVar1 = 0;
  }
  return uVar1;
}

