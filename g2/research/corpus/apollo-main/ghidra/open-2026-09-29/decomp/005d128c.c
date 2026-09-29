
int FUN_005d128c(undefined4 *param_1,int param_2,int param_3,int param_4,char param_5)

{
  int iVar1;
  
  *(undefined1 *)(param_1 + 0x10) = 0;
  *(undefined1 *)((int)param_1 + 0x41) = 1;
  param_1[1] = param_2;
  param_1[2] = param_4;
  *param_1 = *(undefined4 *)(param_2 + 100);
  if (param_4 != 0) {
    iVar1 = **(int **)(param_4 + 0x9c);
    param_1[3] = iVar1;
    param_1[4] = iVar1 + 0x14;
    param_1[5] = iVar1 + 0x38;
    FT_GlyphLoader_Rewind();
    param_1[0x12] = **(undefined4 **)(param_3 + 0x28);
    param_1[0x11] = 0;
    if (param_5 != '\0') {
      param_1[0x11] = *(undefined4 *)(*(int *)(param_4 + 0x9c) + 0x24);
    }
  }
  param_1[6] = 0;
  param_1[7] = 0;
  param_1[8] = 0;
  param_1[9] = 0;
  param_1[10] = 0;
  param_1[0xb] = 0;
  FUN_00439c04(param_1 + 0x13,DAT_005d1e98,0x20);
  return param_4;
}

