
undefined4 dmConnSmActConnFailed(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  dmConnCcbDealloc(param_1);
  if (*(char *)(param_1 + 0x19) == '\0') {
    dmDevPassEvtToDevPriv(0xe,1,0,0);
    iVar1 = dmConnNum();
    if (iVar1 == 0) {
      dmDevPassEvtToDevPriv(0xd,0x28,0,0);
    }
  }
  *(undefined1 *)(param_2 + 2) = 0x28;
  *(undefined1 *)(param_2 + 8) = 0;
  *(ushort *)(param_2 + 6) = (ushort)*(byte *)(param_2 + 8);
  dmConnExecCback(param_2);
  return param_4;
}

