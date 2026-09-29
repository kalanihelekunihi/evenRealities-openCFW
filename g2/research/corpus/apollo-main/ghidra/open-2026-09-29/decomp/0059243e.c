
undefined4 FUN_0059243e(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00592650)) {
    uVar1 = 2;
  }
  else {
    *(undefined4 *)(DAT_00592640 + param_1[2] * 0x1000 + 0x18) = 1;
    uVar1 = 0;
  }
  return uVar1;
}

