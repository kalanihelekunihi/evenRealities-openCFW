
void ft_set_current_renderer(int param_1)

{
  undefined4 uVar1;
  
  uVar1 = FT_Lookup_Renderer(param_1,DAT_00527500,0);
  *(undefined4 *)(param_1 + 0x9c) = uVar1;
  return;
}

