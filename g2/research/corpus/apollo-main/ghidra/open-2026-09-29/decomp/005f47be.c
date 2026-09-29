
int GetShortIns(int param_1)

{
  *(int *)(param_1 + 0x16c) = *(int *)(param_1 + 0x16c) + 2;
  return (int)(short)((ushort)*(byte *)(*(int *)(param_1 + 0x168) + *(int *)(param_1 + 0x16c) + -2)
                      * 0x100 +
                     (ushort)*(byte *)(*(int *)(param_1 + 0x16c) + *(int *)(param_1 + 0x168) + -1));
}

