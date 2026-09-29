
undefined4 dmConnSmActConnOpened(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  undefined4 uVar2;
  int iVar3;
  
  FUN_004d293c(param_1,param_2 + 10);
  *(undefined2 *)(param_1 + 0xc) = *(undefined2 *)(param_2 + 6);
  uVar1 = DmHostAddrType(*(undefined1 *)(param_2 + 9));
  *(undefined1 *)(param_1 + 0x13) = uVar1;
  *(undefined1 *)(param_1 + 0x19) = *(undefined1 *)(param_2 + 8);
  if (*(char *)(param_1 + 0x19) == '\0') {
    *(undefined1 *)(param_1 + 0x14) = *(undefined1 *)(DAT_004b6f20 + 0xd);
  }
  else {
    *(undefined1 *)(param_1 + 0x14) = *(undefined1 *)(DAT_004b6f20 + 0xe);
  }
  if (*(char *)(param_1 + 0x14) == '\0') {
    uVar2 = HciGetBdAddr();
    FUN_004d293c(param_1 + 6,uVar2);
  }
  else {
    FUN_004d293c(param_1 + 6,DAT_004b6f20);
  }
  FUN_004d293c(param_1 + 0x1a,param_2 + 0x17);
  FUN_004d293c(param_1 + 0x20,param_2 + 0x1d);
  *(undefined2 *)(param_1 + 0xe) = 0;
  if (*(char *)(param_1 + 0x19) == '\0') {
    dmDevPassEvtToDevPriv(0xe,1,0,0);
    iVar3 = dmConnNum();
    if (iVar3 == 1) {
      dmDevPassEvtToDevPriv(0xc,0x27,0,0);
    }
  }
  dmDevPassEvtToConnCte(0x27,*(undefined1 *)(param_1 + 0x10));
  *(undefined1 *)(param_2 + 2) = 0x27;
  dmConnExecCback(param_2);
  return param_4;
}

