
int TT_Access_Glyph_Frame(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_1 + 0x18);
  iVar1 = FT_Stream_Seek(iVar2,param_3);
  if ((iVar1 == 0) && (iVar1 = FT_Stream_EnterFrame(iVar2,param_4), iVar1 == 0)) {
    *(undefined4 *)(param_1 + 0xc4) = *(undefined4 *)(iVar2 + 0x20);
    *(undefined4 *)(param_1 + 200) = *(undefined4 *)(iVar2 + 0x24);
    iVar1 = 0;
  }
  return iVar1;
}

