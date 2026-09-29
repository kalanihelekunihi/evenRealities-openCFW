
undefined8 FT_Stream_New(undefined4 *param_1,byte *param_2,int *param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int local_18;
  
  *param_3 = 0;
  local_18 = param_4;
  if (param_1 == (undefined4 *)0x0) {
    iVar2 = 0x21;
  }
  else if (param_2 == (byte *)0x0) {
    iVar2 = 6;
  }
  else {
    uVar3 = *param_1;
    iVar1 = ft_mem_alloc(uVar3,0x28,&local_18);
    iVar2 = local_18;
    if (local_18 == 0) {
      *(undefined4 *)(iVar1 + 0x1c) = uVar3;
      if ((int)((uint)*param_2 << 0x1f) < 0) {
        FT_Stream_OpenMemory(iVar1,*(undefined4 *)(param_2 + 4),*(undefined4 *)(param_2 + 8));
      }
      else if ((int)((uint)*param_2 << 0x1d) < 0) {
        local_18 = FUN_005675e8(iVar1,*(undefined4 *)(param_2 + 0xc));
        *(undefined4 *)(iVar1 + 0x10) = *(undefined4 *)(param_2 + 0xc);
      }
      else if (((int)((uint)*param_2 << 0x1e) < 0) && (*(int *)(param_2 + 0x10) != 0)) {
        ft_mem_free(uVar3,iVar1);
        iVar1 = *(int *)(param_2 + 0x10);
      }
      else {
        local_18 = 6;
      }
      if (local_18 == 0) {
        *(undefined4 *)(iVar1 + 0x1c) = uVar3;
      }
      else {
        ft_mem_free(uVar3,iVar1);
        iVar1 = 0;
      }
      *param_3 = iVar1;
      iVar2 = local_18;
    }
  }
  return CONCAT44(local_18,iVar2);
}

