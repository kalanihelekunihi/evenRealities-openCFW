
undefined4 FT_Done_Face(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar2 = 0x23;
  if ((param_1 != 0) && (*(int *)(param_1 + 0x60) != 0)) {
    *(int *)(*(int *)(param_1 + 0x80) + 0x40) = *(int *)(*(int *)(param_1 + 0x80) + 0x40) + -1;
    if (*(int *)(*(int *)(param_1 + 0x80) + 0x40) < 1) {
      iVar3 = *(int *)(param_1 + 0x60);
      uVar4 = *(undefined4 *)(iVar3 + 8);
      iVar1 = FT_List_Find(iVar3 + 0x10,param_1);
      if (iVar1 != 0) {
        FT_List_Remove(iVar3 + 0x10,iVar1);
        ft_mem_free(uVar4,iVar1);
        destroy_face(uVar4,param_1,iVar3);
        uVar2 = 0;
      }
    }
    else {
      uVar2 = 0;
    }
  }
  return uVar2;
}

