
undefined4 destroy_face(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = *(int *)(param_3 + 0xc);
  if (*(int *)(param_2 + 0x78) != 0) {
    (**(code **)(param_2 + 0x78))(*(undefined4 *)(param_2 + 0x74));
  }
  while (*(int *)(param_2 + 0x54) != 0) {
    FT_Done_GlyphSlot(*(undefined4 *)(param_2 + 0x54));
  }
  FT_List_Finalize(param_2 + 0x6c,DAT_0052629c,param_1,param_3);
  *(undefined4 *)(param_2 + 0x58) = 0;
  if (*(int *)(param_2 + 0x30) != 0) {
    (**(code **)(param_2 + 0x30))(param_2);
  }
  destroy_charmaps(param_2,param_1);
  if (*(int *)(iVar1 + 0x34) != 0) {
    (**(code **)(iVar1 + 0x34))(param_2);
  }
  FT_Stream_Free(*(undefined4 *)(param_2 + 0x68),*(int *)(param_2 + 8) >> 10 & 1);
  *(undefined4 *)(param_2 + 0x68) = 0;
  if (*(int *)(param_2 + 0x80) != 0) {
    ft_mem_free(param_1,*(undefined4 *)(param_2 + 0x80));
    *(undefined4 *)(param_2 + 0x80) = 0;
  }
  ft_mem_free(param_1,param_2);
  return param_4;
}

