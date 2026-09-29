
int FUN_005dd780(int param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  byte *pbVar4;
  uint uVar5;
  
  iVar1 = *(int *)(param_1 + 0x10);
  uVar2 = (uint)*(byte *)(iVar1 + 0x200f) |
          (uint)*(byte *)(iVar1 + 0x200d) << 0x10 | (uint)*(byte *)(iVar1 + 0x200c) << 0x18 |
          (uint)*(byte *)(iVar1 + 0x200e) << 8;
  pbVar4 = (byte *)(iVar1 + 0x2010);
  while( true ) {
    if (uVar2 == 0) {
      return 0;
    }
    uVar3 = (uint)pbVar4[3] | (uint)pbVar4[1] << 0x10 | (uint)*pbVar4 << 0x18 | (uint)pbVar4[2] << 8
    ;
    uVar5 = (uint)pbVar4[0xb] |
            (uint)pbVar4[9] << 0x10 | (uint)pbVar4[8] << 0x18 | (uint)pbVar4[10] << 8;
    if (param_2 < uVar3) break;
    if (param_2 <=
        ((uint)pbVar4[7] | (uint)pbVar4[5] << 0x10 | (uint)pbVar4[4] << 0x18 | (uint)pbVar4[6] << 8)
       ) {
      if (uVar5 <= uVar3 + (-1 - param_2)) {
        return (param_2 + uVar5) - uVar3;
      }
      return 0;
    }
    uVar2 = uVar2 - 1;
    pbVar4 = pbVar4 + 0xc;
  }
  return 0;
}

