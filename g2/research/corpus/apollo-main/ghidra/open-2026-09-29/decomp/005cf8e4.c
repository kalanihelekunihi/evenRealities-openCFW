
uint FUN_005cf8e4(uint *param_1)

{
  uint uVar1;
  byte *pbVar2;
  
  if ((int)param_1[3] < 1) {
    do {
      if (*param_1 < param_1[2]) {
        pbVar2 = (byte *)*param_1;
        *param_1 = (uint)(pbVar2 + 1);
        uVar1 = (uint)*pbVar2;
      }
      else {
        uVar1 = 0xffffffff;
      }
    } while ((uVar1 == 0x20) || (uVar1 == 9));
    if ((uVar1 == 0xd) || (uVar1 == 10)) {
      param_1[3] = 2;
    }
    else if (uVar1 == 0x3b) {
      param_1[3] = 1;
    }
    else if ((uVar1 == 0xffffffff) || (uVar1 == 0x1a)) {
      param_1[3] = 3;
    }
  }
  else {
    uVar1 = 0x3b;
  }
  return uVar1;
}

