
undefined4 FUN_0055c518(uint *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055cc14)) {
    uVar1 = 2;
  }
  else {
    *(undefined4 *)(DAT_0055c548 + param_1[1] * 0x1000 + 0x208) = param_2;
    uVar1 = 0;
  }
  return uVar1;
}

