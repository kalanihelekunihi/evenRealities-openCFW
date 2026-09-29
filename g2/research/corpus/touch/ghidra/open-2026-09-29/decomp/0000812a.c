
uint GetReadRowPointer(uint param_1,ushort *param_2)

{
  int iVar1;
  
  if (1 < (byte)param_2[6]) {
    iVar1 = (uint)*param_2 * (uint)param_2[1];
    if (param_1 < (uint)(*(int *)(param_2 + 8) + iVar1)) {
      param_1 = param_1 + ((byte)param_2[6] - 1) * iVar1;
    }
    else {
      param_1 = param_1 - iVar1;
    }
  }
  return param_1;
}

