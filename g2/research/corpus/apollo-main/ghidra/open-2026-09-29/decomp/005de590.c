
undefined4 FUN_005de590(byte *param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = 0;
  uVar3 = (uint)param_1[3] |
          (uint)param_1[1] << 0x10 | (uint)*param_1 << 0x18 | (uint)param_1[2] << 8;
  while( true ) {
    do {
      uVar1 = uVar3;
      if (uVar1 <= uVar2) {
        return 0;
      }
      uVar3 = uVar1 + uVar2 >> 1;
      uVar4 = (uint)param_1[uVar3 * 4 + 6] |
              (uint)param_1[uVar3 * 4 + 5] << 8 | (uint)param_1[uVar3 * 4 + 4] << 0x10;
    } while (param_2 < uVar4);
    if (param_2 <= param_1[uVar3 * 4 + 7] + uVar4) break;
    uVar2 = uVar3 + 1;
    uVar3 = uVar1;
  }
  return 1;
}

