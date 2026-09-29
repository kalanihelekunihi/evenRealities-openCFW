
undefined8 FUN_0055c286(uint *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055cc14)) {
    uVar1 = 2;
  }
  else {
    if ((int)(*param_1 << 6) < 0) {
      FUN_0055c430();
    }
    *param_1 = *param_1 & 0xfeffffff;
    uVar1 = 0;
  }
  return CONCAT44(param_4,uVar1);
}

