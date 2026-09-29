
int FUN_0041b25c(undefined1 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 *local_14;
  int local_10;
  int local_c;
  undefined4 uStack_8;
  
  local_c = 0;
  if (param_2 == 0) {
    local_14 = (undefined1 *)0x0;
    local_10 = 0;
  }
  else {
    local_10 = param_2 + -1;
    local_14 = param_1;
  }
  uStack_8 = param_4;
  iVar1 = FUN_0041e47a((int)&DAT_0041b294 + DAT_0041b294,&local_14,param_3,&uStack_8,0);
  if (local_14 != (undefined1 *)0x0) {
    *local_14 = 0;
  }
  if (-1 < iVar1) {
    iVar1 = local_c;
  }
  return iVar1;
}

