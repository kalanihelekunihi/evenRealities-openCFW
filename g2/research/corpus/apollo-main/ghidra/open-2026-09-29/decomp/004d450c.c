
undefined4 FUN_004d450c(byte *param_1,uint param_2)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  if (*DAT_004d4604 << 0x1f < 0) {
    uVar1 = 3;
  }
  else {
    for (uVar4 = 0; uVar4 < param_2; uVar4 = uVar4 + 1) {
      if (7 < *param_1) {
        return 5;
      }
      if (param_1[1] == 0) {
        uVar2 = 0;
        uVar3 = (uint)param_1[10] << 2;
      }
      else {
        uVar2 = (uint)param_1[5] |
                (uint)param_1[3] << 2 | (uint)param_1[2] << 3 | (uint)param_1[4] << 1;
        uVar3 = (uint)param_1[9] |
                (uint)param_1[7] << 2 | (uint)param_1[6] << 3 | (uint)param_1[8] << 1;
      }
      if ((uVar2 & 0xf) == 0) {
        uVar3 = (uVar3 & 3) << 2;
      }
      else {
        uVar3 = uVar3 & 0xf;
      }
      FUN_004d4434(*param_1,uVar3 | (uVar2 & 0xf) << 4);
      param_1 = param_1 + 0xb;
    }
    uVar1 = 0;
  }
  return uVar1;
}

