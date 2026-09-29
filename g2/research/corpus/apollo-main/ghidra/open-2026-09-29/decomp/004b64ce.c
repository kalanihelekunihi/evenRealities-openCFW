
undefined4 dmConnSmActConnClosed(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  dmDevPassEvtToConnCte(0x28,*(undefined1 *)(param_1 + 0x10));
  dmConnCcbDealloc(param_1);
  if ((*(char *)(param_1 + 0x19) == '\0') && (iVar1 = dmConnNum(), iVar1 == 0)) {
    dmDevPassEvtToDevPriv(0xd,0x28,0,0);
  }
  *(undefined1 *)(param_2 + 2) = 0x28;
  dmConnExecCback(param_2);
  return param_4;
}

