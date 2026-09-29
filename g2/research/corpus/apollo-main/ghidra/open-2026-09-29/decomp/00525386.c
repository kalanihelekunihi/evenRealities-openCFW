
undefined8 FT_New_GlyphSlot(int param_1,int *param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int local_18;
  
  if (param_1 == 0) {
    iVar2 = 0x23;
    local_18 = param_4;
  }
  else if (*(int *)(param_1 + 0x60) == 0) {
    iVar2 = 6;
    local_18 = param_4;
  }
  else {
    uVar3 = *(undefined4 *)(*(int *)(param_1 + 0x60) + 8);
    local_18 = param_4;
    iVar1 = ft_mem_alloc(uVar3,*(undefined4 *)(*(int *)(*(int *)(param_1 + 0x60) + 0xc) + 0x2c),
                         &local_18);
    if (local_18 == 0) {
      *(int *)(iVar1 + 4) = param_1;
      iVar2 = ft_glyphslot_init(iVar1);
      local_18 = iVar2;
      if (iVar2 == 0) {
        *(undefined4 *)(iVar1 + 8) = *(undefined4 *)(param_1 + 0x54);
        *(int *)(param_1 + 0x54) = iVar1;
        if (param_2 != (int *)0x0) {
          *param_2 = iVar1;
        }
      }
      else {
        ft_glyphslot_done(iVar1);
        ft_mem_free(uVar3,iVar1);
        iVar2 = local_18;
      }
    }
    else {
      iVar2 = local_18;
      if (param_2 != (int *)0x0) {
        *param_2 = 0;
      }
    }
  }
  return CONCAT44(local_18,iVar2);
}

