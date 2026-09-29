
undefined4 Direct_Move_Orig(int param_1,int param_2,ushort param_3,undefined4 param_4)

{
  int iVar1;
  
  if (*(short *)(param_1 + 0x12e) != 0) {
    iVar1 = FT_MulDiv(param_4,(int)*(short *)(param_1 + 0x12e),*(undefined4 *)(param_1 + 0x238));
    *(int *)(*(int *)(param_2 + 0xc) + (uint)param_3 * 8) =
         iVar1 + *(int *)(*(int *)(param_2 + 0xc) + (uint)param_3 * 8);
  }
  if (*(short *)(param_1 + 0x130) != 0) {
    iVar1 = FT_MulDiv(param_4,(int)*(short *)(param_1 + 0x130),*(undefined4 *)(param_1 + 0x238));
    *(int *)(*(int *)(param_2 + 0xc) + (uint)param_3 * 8 + 4) =
         iVar1 + *(int *)(*(int *)(param_2 + 0xc) + (uint)param_3 * 8 + 4);
  }
  return param_4;
}

