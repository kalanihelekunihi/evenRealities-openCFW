
undefined8 raccess_make_file_name(undefined4 param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  undefined1 *puVar3;
  int local_18;
  
  local_18 = 0;
  iVar1 = FUN_0044a43c(param_2);
  iVar2 = FUN_0044a43c(param_3);
  puVar3 = (undefined1 *)ft_mem_alloc(param_1,iVar2 + iVar1 + 1,&local_18);
  if (local_18 == 0) {
    iVar1 = FUN_00567c64(param_2,0x2f);
    if (iVar1 == 0) {
      *puVar3 = 0;
    }
    else {
      FUN_0044b5a0(puVar3,param_2,(iVar1 - param_2) + 1);
      puVar3[(iVar1 - param_2) + 1] = 0;
      param_2 = iVar1 + 1;
    }
    FUN_00567c80(puVar3,param_3);
    FUN_00567c80(puVar3,param_2);
  }
  else {
    puVar3 = (undefined1 *)0x0;
  }
  return CONCAT44(local_18,puVar3);
}

