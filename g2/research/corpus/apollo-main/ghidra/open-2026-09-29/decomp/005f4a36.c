
void Direct_Move_Orig_X(undefined4 param_1,int param_2,ushort param_3,int param_4)

{
  *(int *)(*(int *)(param_2 + 0xc) + (uint)param_3 * 8) =
       param_4 + *(int *)(*(int *)(param_2 + 0xc) + (uint)param_3 * 8);
  return;
}

