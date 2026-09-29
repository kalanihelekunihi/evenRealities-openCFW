
undefined4 FT_Done_GlyphSlot(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  if (param_1 != 0) {
    uVar4 = *(undefined4 *)(*(int *)(*(int *)(param_1 + 4) + 0x60) + 8);
    iVar1 = *(int *)(*(int *)(param_1 + 4) + 0x54);
    iVar3 = 0;
    while (iVar2 = iVar1, iVar2 != 0) {
      if (iVar2 == param_1) {
        if (iVar3 == 0) {
          *(undefined4 *)(*(int *)(param_1 + 4) + 0x54) = *(undefined4 *)(iVar2 + 8);
        }
        else {
          *(undefined4 *)(iVar3 + 8) = *(undefined4 *)(iVar2 + 8);
        }
        if (*(int *)(param_1 + 0x14) != 0) {
          (**(code **)(param_1 + 0x14))(param_1);
        }
        ft_glyphslot_done(param_1);
        ft_mem_free(uVar4,param_1);
        return param_4;
      }
      iVar3 = iVar2;
      iVar1 = *(int *)(iVar2 + 8);
    }
  }
  return param_4;
}

