
void ft_glyphslot_done(int param_1)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(*(int *)(param_1 + 4) + 0x60);
  uVar1 = puVar2[2];
  if (*(int *)(puVar2[3] + 0x44) != 0) {
    (**(code **)(puVar2[3] + 0x44))(param_1);
  }
  ft_glyphslot_free_bitmap(param_1);
  if (*(int *)(param_1 + 0x9c) != 0) {
    if (-1 < *(int *)*puVar2 << 0x16) {
      FT_GlyphLoader_Done(**(undefined4 **)(param_1 + 0x9c));
      **(undefined4 **)(param_1 + 0x9c) = 0;
    }
    ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0x9c));
    *(undefined4 *)(param_1 + 0x9c) = 0;
  }
  return;
}

