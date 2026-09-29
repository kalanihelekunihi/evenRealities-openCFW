
void Direct_Move_Y(int *param_1,int param_2,ushort param_3,int param_4)

{
  if ((((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) != 0x28) ||
       (*(char *)((int)param_1 + 0x267) == '\0')) || ((char)param_1[0x9a] == '\0')) ||
     (*(char *)((int)param_1 + 0x269) == '\0')) {
    *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8 + 4) =
         param_4 + *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8 + 4);
  }
  *(byte *)(*(int *)(param_2 + 0x18) + (uint)param_3) =
       *(byte *)(*(int *)(param_2 + 0x18) + (uint)param_3) | 0x10;
  return;
}

