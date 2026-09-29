
void Direct_Move_X(int *param_1,int param_2,ushort param_3,int param_4)

{
  if ((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x28) &&
     (*(char *)((int)param_1 + 0x267) == '\0')) {
    *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8) =
         param_4 + *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8);
  }
  else if (*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x23) {
    *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8) =
         param_4 + *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8);
  }
  *(byte *)(*(int *)(param_2 + 0x18) + (uint)param_3) =
       *(byte *)(*(int *)(param_2 + 0x18) + (uint)param_3) | 8;
  return;
}

