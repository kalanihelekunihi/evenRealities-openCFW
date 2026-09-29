
undefined4 FUN_00423700(uint *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00423830)) {
    uVar1 = 2;
  }
  else {
    *(undefined4 *)(DAT_00423764 + param_1[10] * 0x1000 + 0x44) = param_2;
    uVar1 = 0;
  }
  return uVar1;
}

