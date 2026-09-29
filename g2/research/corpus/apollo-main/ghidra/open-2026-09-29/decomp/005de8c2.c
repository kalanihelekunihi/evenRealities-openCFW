
int FUN_005de8c2(byte *param_1)

{
  int iVar1;
  uint uVar2;
  byte *pbVar3;
  
  iVar1 = 0;
  pbVar3 = param_1 + 7;
  for (uVar2 = (uint)param_1[3] |
               (uint)param_1[1] << 0x10 | (uint)*param_1 << 0x18 | (uint)param_1[2] << 8; uVar2 != 0
      ; uVar2 = uVar2 - 1) {
    iVar1 = *pbVar3 + 1 + iVar1;
    pbVar3 = pbVar3 + 4;
  }
  return iVar1;
}

