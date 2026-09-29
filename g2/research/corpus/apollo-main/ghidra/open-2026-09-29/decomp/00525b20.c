
undefined8
new_memory_stream(undefined4 *param_1,int param_2,int param_3,undefined4 param_4,int *param_5)

{
  int iVar1;
  int iVar2;
  int local_20;
  undefined4 uStack_1c;
  
  local_20 = param_3;
  if (param_1 == (undefined4 *)0x0) {
    iVar2 = 0x21;
  }
  else if (param_2 == 0) {
    iVar2 = 6;
  }
  else {
    *param_5 = 0;
    uStack_1c = param_4;
    iVar1 = ft_mem_alloc(*param_1,0x28,&local_20);
    iVar2 = local_20;
    if (local_20 == 0) {
      FT_Stream_OpenMemory(iVar1,param_2,param_3);
      *(undefined4 *)(iVar1 + 0x18) = param_4;
      *param_5 = iVar1;
      iVar2 = local_20;
    }
  }
  return CONCAT44(local_20,iVar2);
}

