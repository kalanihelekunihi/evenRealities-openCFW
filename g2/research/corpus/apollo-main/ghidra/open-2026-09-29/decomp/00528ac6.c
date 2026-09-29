
uint FT_Stream_GetULong(int param_1)

{
  uint uVar1;
  byte *pbVar2;
  byte *pbVar3;
  
  uVar1 = 0;
  pbVar2 = *(byte **)(param_1 + 0x20);
  pbVar3 = pbVar2;
  if (pbVar2 + 3 < *(byte **)(param_1 + 0x24)) {
    pbVar3 = pbVar2 + 4;
    uVar1 = (uint)pbVar2[3] | (uint)pbVar2[1] << 0x10 | (uint)*pbVar2 << 0x18 | (uint)pbVar2[2] << 8
    ;
  }
  *(byte **)(param_1 + 0x20) = pbVar3;
  return uVar1;
}

