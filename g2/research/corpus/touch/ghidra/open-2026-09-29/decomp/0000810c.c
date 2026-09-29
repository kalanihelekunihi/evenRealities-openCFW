
uint GetNextRowPointer(int param_1,ushort *param_2)

{
  uint uVar1;
  
  uVar1 = param_1 + (uint)(param_2[1] >> 2) * 4;
  if ((uint)param_2[1] * (uint)*param_2 * (uint)(byte)param_2[6] + *(uint *)(param_2 + 8) <= uVar1)
  {
    uVar1 = *(uint *)(param_2 + 8);
  }
  return uVar1;
}

