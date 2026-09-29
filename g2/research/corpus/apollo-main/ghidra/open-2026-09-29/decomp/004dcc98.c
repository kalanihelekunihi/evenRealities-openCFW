
uint FUN_004dcc98(int param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = 0xffff;
  for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
    uVar1 = uVar1 ^ *(byte *)(param_1 + uVar3);
    for (iVar2 = 0; iVar2 < 8; iVar2 = iVar2 + 1) {
      if ((int)(uVar1 << 0x1f) < 0) {
        uVar1 = uVar1 >> 1 ^ 0xa001;
      }
      else {
        uVar1 = uVar1 >> 1;
      }
    }
  }
  return uVar1;
}

