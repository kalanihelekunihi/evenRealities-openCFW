
void AttsSetCsrk(undefined1 param_1,undefined4 param_2,undefined1 param_3)

{
  int iVar1;
  
  iVar1 = attsSignCcbByConnId(param_1);
  *(undefined4 *)(iVar1 + 4) = param_2;
  iVar1 = attsSignCcbByConnId(param_1);
  *(undefined1 *)(iVar1 + 0xc) = param_3;
  return;
}

