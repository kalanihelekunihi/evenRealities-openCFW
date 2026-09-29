
void case_update_cached_byte(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_14;
  
  iVar1 = DAT_08009a10;
  local_14._0_1_ = (char)param_2;
  if ((*(char *)(DAT_08009a10 + param_1) != (char)local_14) &&
     (local_14 = param_2, iVar2 = FUN_08009108(param_1,1,&local_14,param_4,param_1), iVar2 != 0)) {
    *(char *)(iVar1 + param_1) = (char)local_14;
  }
  return;
}

