
int FUN_004b4728(undefined1 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 *local_1c;
  undefined4 *local_18;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  local_18 = &uStack_8;
  local_1c = param_1;
  uStack_8 = param_3;
  uStack_4 = param_4;
  iVar1 = FUN_00481836((int)&DAT_004b4764 + DAT_004b4764,&local_1c,param_2,&local_18,0);
  *local_1c = 0;
  if (-1 < iVar1) {
    iVar1 = (int)local_1c - (int)param_1;
  }
  return iVar1;
}

