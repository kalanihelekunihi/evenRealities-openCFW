
void cff_font_done(int param_1)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar1 = *(undefined4 *)(param_1 + 8);
  cff_index_done(param_1 + 0x6c);
  cff_index_done(param_1 + 0x4d8);
  cff_index_done(param_1 + 0x24);
  cff_index_done(param_1 + 0x4b4);
  if (*(int *)(param_1 + 0x7e8) != 0) {
    for (uVar2 = 0; uVar2 < *(uint *)(param_1 + 0x7e8); uVar2 = uVar2 + 1) {
      cff_subfont_done(uVar1,*(undefined4 *)(param_1 + uVar2 * 4 + 0x7ec));
    }
    ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0x7ec));
    *(undefined4 *)(param_1 + 0x7ec) = 0;
  }
  cff_encoding_done(param_1 + 0x90);
  cff_charset_done(param_1 + 0x49c,*(undefined4 *)(param_1 + 4));
  cff_vstore_done(param_1 + 0xc28,uVar1);
  cff_subfont_done(uVar1,param_1 + 0x55c);
  CFF_Done_FD_Select(param_1 + 0xbec,*(undefined4 *)(param_1 + 4));
  ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0xc14));
  *(undefined4 *)(param_1 + 0xc14) = 0;
  ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0x544));
  *(undefined4 *)(param_1 + 0x544) = 0;
  ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0x548));
  *(undefined4 *)(param_1 + 0x548) = 0;
  ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0x550));
  *(undefined4 *)(param_1 + 0x550) = 0;
  ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0x554));
  *(undefined4 *)(param_1 + 0x554) = 0;
  if (*(int *)(param_1 + 0xc24) != 0) {
    (**(code **)(param_1 + 0xc24))(*(undefined4 *)(param_1 + 0xc20));
    ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0xc20));
    *(undefined4 *)(param_1 + 0xc20) = 0;
  }
  ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0xc3c));
  *(undefined4 *)(param_1 + 0xc3c) = 0;
  return;
}

