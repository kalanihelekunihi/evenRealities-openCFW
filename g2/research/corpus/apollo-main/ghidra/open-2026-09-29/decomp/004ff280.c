
uint FUN_004ff280(float param_1,float param_2,float param_3)

{
  uint uVar1;
  
  param_3 = (param_1 - param_2) * param_3;
  if ((int)((uint)(param_3 < 0.0) << 0x1f) < 0) {
    uVar1 = 0;
  }
  else if (param_3 < DAT_004ff48c) {
    uVar1 = (int)param_3 & 0xff;
  }
  else {
    uVar1 = 0x3d;
  }
  return uVar1;
}

