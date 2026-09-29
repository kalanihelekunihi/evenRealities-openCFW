
uint __module_get_div_isra_1(int param_1,int param_2)

{
  byte *pbVar1;
  uint uVar2;
  
  pbVar1 = *(byte **)(param_1 + 8);
  uVar2 = 0;
  if ((pbVar1 != (byte *)0x0) &&
     (uVar2 = (uint)*(ushort *)(pbVar1 + 2) &
              *(uint *)(param_2 + (uint)*pbVar1) >> (pbVar1[1] & 0x3f), uVar2 != 0)) {
    uVar2 = uVar2 + 1;
  }
  return uVar2;
}

