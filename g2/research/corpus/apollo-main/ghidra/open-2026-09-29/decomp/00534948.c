
int DmSecGetCompareValue(int param_1)

{
  uint uVar1;
  
  uVar1 = (uint)*(byte *)(param_1 + 0xe) * 0x100 + (uint)*(byte *)(param_1 + 0xf) +
          (uint)*(byte *)(param_1 + 0xd) * 0x10000 + (uint)*(byte *)(param_1 + 0xc) * 0x1000000;
  return uVar1 - DAT_00534980 * (uVar1 / DAT_00534980);
}

