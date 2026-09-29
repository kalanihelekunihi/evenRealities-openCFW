
int cff_size_init(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int local_e8;
  undefined1 auStack_e4 [196];
  undefined4 uStack_20;
  
  local_e8 = 0;
  uStack_20 = param_4;
  puVar1 = (undefined4 *)cff_size_get_globals_funcs(param_1);
  if (puVar1 != (undefined4 *)0x0) {
    iVar5 = *(int *)(*param_1 + 0x2a4);
    iVar2 = ft_mem_alloc(*(undefined4 *)(*param_1 + 100),0x404,&local_e8);
    if (local_e8 != 0) {
      return local_e8;
    }
    cff_make_private_dict(iVar5 + 0x55c,auStack_e4);
    iVar3 = (*(code *)*puVar1)(*(undefined4 *)(*param_1 + 100),auStack_e4,iVar2);
    if (iVar3 != 0) {
      return iVar3;
    }
    for (iVar3 = *(int *)(iVar5 + 0x7e8); local_e8 = 0, iVar3 != 0; iVar3 = iVar3 + -1) {
      cff_make_private_dict(*(undefined4 *)(iVar5 + iVar3 * 4 + 0x7e8),auStack_e4);
      iVar4 = (*(code *)*puVar1)(*(undefined4 *)(*param_1 + 100),auStack_e4,iVar2 + iVar3 * 4);
      if (iVar4 != 0) {
        return iVar4;
      }
    }
    *(int *)param_1[10] = iVar2;
  }
  param_1[0xb] = -1;
  return local_e8;
}

