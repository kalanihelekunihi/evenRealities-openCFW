
undefined4 cff_get_is_cid(int param_1,undefined1 *param_2)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x2a4);
  *param_2 = 0;
  if ((iVar1 != 0) && (*(int *)(iVar1 + 0x5e0) != 0xffff)) {
    *param_2 = 1;
  }
  return 0;
}

