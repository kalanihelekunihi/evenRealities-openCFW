
uint FUN_00545868(int param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  
  uVar1 = 0xffff;
  for (uVar2 = 0; uVar2 < param_2; uVar2 = uVar2 + 1) {
    uVar1 = uVar1 ^ (uint)*(byte *)(param_1 + uVar2) << 8;
    for (iVar3 = 0; iVar3 < 8; iVar3 = iVar3 + 1) {
      if ((int)(uVar1 << 0x10) < 0) {
        uVar1 = uVar1 << 1 ^ 0x1021;
      }
      else {
        uVar1 = uVar1 << 1;
      }
    }
  }
  return uVar1 & 0xffff;
}

