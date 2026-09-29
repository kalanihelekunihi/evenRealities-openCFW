
undefined4 FUN_00590818(uint *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00590a20)) {
    uVar1 = 2;
  }
  else {
    *(undefined4 *)(DAT_00590d34 + param_1[1] * 0x1000 + 0x308) = param_2;
    uVar1 = 0;
  }
  return uVar1;
}

