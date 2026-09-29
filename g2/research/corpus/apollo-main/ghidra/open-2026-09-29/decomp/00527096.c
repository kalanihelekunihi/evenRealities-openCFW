
void ft_lookup_glyph_renderer(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *(int *)(*(int *)(*(int *)(param_1 + 4) + 0x60) + 4);
  iVar1 = *(int *)(iVar2 + 0x9c);
  if ((iVar1 == 0) || (*(int *)(iVar1 + 0x10) != *(int *)(param_1 + 0x48))) {
    FT_Lookup_Renderer(iVar2,*(undefined4 *)(param_1 + 0x48),0);
  }
  return;
}

