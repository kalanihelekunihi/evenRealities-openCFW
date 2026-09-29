
undefined4 FUN_004c0f24(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004c0f68)) {
    uVar1 = 2;
  }
  else {
    if ((int)(*param_1 << 6) < 0) {
      FUN_004c0ea8();
    }
    *param_1 = *param_1 & 0xfeffffff;
    param_1[1] = 0;
    uVar1 = 0;
  }
  return uVar1;
}

