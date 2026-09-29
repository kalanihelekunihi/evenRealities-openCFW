
undefined4 FUN_0053456c(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_004bb07c(param_1);
  if ((iVar1 != 0) && (iVar2 = FUN_0047ae78(iVar1,8,0), iVar2 != 0)) {
    AttsSetCsrk(param_1,iVar2,0);
    AttsSetSignCounter(param_1,*(undefined4 *)(iVar1 + 0x80));
  }
  return param_4;
}

