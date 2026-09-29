
undefined8 FUN_00539944(uint *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;
  uint local_10;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00539dac)) {
    uVar1 = 2;
    local_10 = param_4;
  }
  else {
    uVar1 = 0;
    local_10 = param_4 & 0xffffff00;
    if ((int)(*param_1 << 6) < 0) {
      uVar1 = FUN_00539a10();
    }
    FUN_004800e4(&local_10);
    if ((local_10 & 0xff) != 0) {
      FUN_0048009e();
    }
    *param_1 = *param_1 & 0xfeffffff;
  }
  return CONCAT44(local_10,uVar1);
}

