
void Move_Zp2_Point(int *param_1,ushort param_2,int param_3,int param_4,char param_5)

{
  if (*(short *)((int)param_1 + 0x12e) != 0) {
    if ((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) != 0x28) ||
       (*(char *)((int)param_1 + 0x267) == '\0')) {
      *(int *)(param_1[0x1f] + (uint)param_2 * 8) =
           param_3 + *(int *)(param_1[0x1f] + (uint)param_2 * 8);
    }
    if (param_5 != '\0') {
      *(byte *)(param_1[0x21] + (uint)param_2) = *(byte *)(param_1[0x21] + (uint)param_2) | 8;
    }
  }
  if ((short)param_1[0x4c] != 0) {
    if ((((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) != 0x28) ||
         (*(char *)((int)param_1 + 0x267) == '\0')) || ((char)param_1[0x9a] == '\0')) ||
       (*(char *)((int)param_1 + 0x269) == '\0')) {
      *(int *)(param_1[0x1f] + (uint)param_2 * 8 + 4) =
           param_4 + *(int *)(param_1[0x1f] + (uint)param_2 * 8 + 4);
    }
    if (param_5 != '\0') {
      *(byte *)(param_1[0x21] + (uint)param_2) = *(byte *)(param_1[0x21] + (uint)param_2) | 0x10;
    }
  }
  return;
}

