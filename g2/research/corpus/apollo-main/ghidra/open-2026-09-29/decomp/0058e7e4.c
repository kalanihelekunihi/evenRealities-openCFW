
undefined4 FUN_0058e7e4(uint *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0058e914)) {
    uVar1 = 2;
  }
  else {
    *(undefined4 *)(DAT_0058e848 + param_1[10] * 0x1000 + 0x44) = param_2;
    uVar1 = 0;
  }
  return uVar1;
}

