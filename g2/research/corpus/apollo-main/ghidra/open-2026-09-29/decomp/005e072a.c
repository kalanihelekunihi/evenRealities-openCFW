
int FUN_005e072a(int *param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = 0x8e;
  iVar2 = *(int *)(param_2 + 0x68);
  iVar3 = *(int *)(*(int *)(param_2 + 0x300) + param_3 * 4);
  if ((*(int *)(param_2 + 0x33c) != 0) &&
     (iVar1 = FT_Stream_Seek(iVar2,*(undefined4 *)(param_2 + 0x338)), iVar1 == 0)) {
    *param_1 = param_2;
    param_1[1] = iVar2;
    param_1[2] = *(int *)(param_2 + 0x54) + 0x4c;
    param_1[3] = param_4;
    *(undefined1 *)(param_1 + 4) = 0;
    *(undefined1 *)((int)param_1 + 0x11) = 0;
    param_1[5] = *(int *)(param_2 + 0x338);
    param_1[6] = *(int *)(param_2 + 0x33c);
    param_1[9] = *(int *)(param_2 + 0x2f0);
    param_1[10] = *(int *)(param_2 + 0x2f0) + *(int *)(param_2 + 0x2f4);
    if (*(uint *)(param_2 + 0x2f4) < iVar3 * 0x30 + 0x37U) {
      iVar1 = 3;
    }
    else {
      iVar2 = param_1[9] + iVar3 * 0x30;
      param_1[7] = (uint)*(byte *)(iVar2 + 9) << 0x10 | (uint)*(byte *)(iVar2 + 8) << 0x18 |
                   (uint)*(byte *)(iVar2 + 10) << 8 | (uint)*(byte *)(iVar2 + 0xb);
      param_1[8] = (uint)*(byte *)(iVar2 + 0x11) << 0x10 | (uint)*(byte *)(iVar2 + 0x10) << 0x18 |
                   (uint)*(byte *)(iVar2 + 0x12) << 8 | (uint)*(byte *)(iVar2 + 0x13);
      *(undefined1 *)((int)param_1 + 0x12) = *(undefined1 *)(iVar2 + 0x36);
      if ((*(uint *)(param_2 + 0x2f4) < (uint)param_1[7]) ||
         ((uint)(*(int *)(param_2 + 0x2f4) - param_1[7]) >> 3 < (uint)param_1[8])) {
        iVar1 = 3;
      }
    }
  }
  return iVar1;
}

