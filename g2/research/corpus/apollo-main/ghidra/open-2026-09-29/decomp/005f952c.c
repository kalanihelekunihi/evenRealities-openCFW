
undefined4 tt_face_free_hdmx(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x68);
  ft_mem_free(*(undefined4 *)(iVar1 + 0x1c),*(undefined4 *)(param_1 + 0x2ec));
  *(undefined4 *)(param_1 + 0x2ec) = 0;
  FT_Stream_ReleaseFrame(iVar1,param_1 + 0x2dc);
  return param_4;
}

