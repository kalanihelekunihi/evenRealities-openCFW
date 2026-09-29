
undefined4 Direct_Move(int *param_1,int param_2,ushort param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = (int)*(short *)((int)param_1 + 0x12e);
  if (iVar1 != 0) {
    if ((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x28) &&
       (*(char *)((int)param_1 + 0x267) == '\0')) {
      iVar1 = FT_MulDiv(param_4,iVar1,param_1[0x8e]);
      *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8) =
           iVar1 + *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8);
    }
    else if (*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x23) {
      iVar1 = FT_MulDiv(param_4,iVar1,param_1[0x8e]);
      *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8) =
           iVar1 + *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8);
    }
    *(byte *)(*(int *)(param_2 + 0x18) + (uint)param_3) =
         *(byte *)(*(int *)(param_2 + 0x18) + (uint)param_3) | 8;
  }
  if ((short)param_1[0x4c] != 0) {
    if ((((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) != 0x28) ||
         (*(char *)((int)param_1 + 0x267) == '\0')) || ((char)param_1[0x9a] == '\0')) ||
       (*(char *)((int)param_1 + 0x269) == '\0')) {
      iVar1 = FT_MulDiv(param_4,(int)(short)param_1[0x4c],param_1[0x8e]);
      *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8 + 4) =
           iVar1 + *(int *)(*(int *)(param_2 + 0x10) + (uint)param_3 * 8 + 4);
    }
    *(byte *)(*(int *)(param_2 + 0x18) + (uint)param_3) =
         *(byte *)(*(int *)(param_2 + 0x18) + (uint)param_3) | 0x10;
  }
  return param_4;
}

