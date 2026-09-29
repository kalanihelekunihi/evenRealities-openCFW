
void FT_Stream_ExtractFrame(int param_1,undefined4 param_2,undefined4 *param_3)

{
  int iVar1;
  
  iVar1 = FT_Stream_EnterFrame(param_1);
  if (iVar1 == 0) {
    *param_3 = *(undefined4 *)(param_1 + 0x20);
    *(undefined4 *)(param_1 + 0x20) = 0;
    *(undefined4 *)(param_1 + 0x24) = 0;
  }
  return;
}

