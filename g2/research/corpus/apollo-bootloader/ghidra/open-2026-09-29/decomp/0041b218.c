
int FUN_0041b218(undefined1 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 *local_24;
  int local_20;
  int local_1c;
  undefined4 *local_18;
  undefined4 uStack_14;
  undefined4 uStack_4;
  
  local_18 = &uStack_4;
  local_1c = 0;
  if (param_2 == 0) {
    local_24 = (undefined1 *)0x0;
    local_20 = 0;
  }
  else {
    local_20 = param_2 + -1;
    local_24 = param_1;
  }
  uStack_14 = param_4;
  uStack_4 = param_4;
  iVar1 = FUN_0041e47a((int)&DAT_0041b258 + DAT_0041b258,&local_24,param_3,&local_18,0);
  if (local_24 != (undefined1 *)0x0) {
    *local_24 = 0;
  }
  if (-1 < iVar1) {
    iVar1 = local_1c;
  }
  return iVar1;
}

