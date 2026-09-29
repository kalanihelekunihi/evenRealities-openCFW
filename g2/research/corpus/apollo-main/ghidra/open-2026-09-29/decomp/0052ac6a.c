
undefined8
HciResetSequence(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  char cVar4;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  piVar3 = DAT_0052ae14;
  uStack_18 = param_3;
  uStack_14 = param_4;
  while( true ) {
    iVar1 = DAT_0052ae18;
    iVar2 = WsfMsgDeq(DAT_0052ae18,&uStack_18);
    if (iVar2 == 0) break;
    WsfMsgFree();
  }
  for (cVar4 = '\x03'; cVar4 != '\0'; cVar4 = cVar4 + -1) {
    if (*piVar3 != 0) {
      WsfMsgFree(*piVar3);
      *piVar3 = 0;
    }
    *(undefined1 *)((int)piVar3 + 0x16) = 0;
    if (piVar3[2] != 0) {
      WsfMsgFree(piVar3[2]);
      piVar3[2] = 0;
    }
    *(undefined2 *)(piVar3 + 4) = 0xffff;
    hciCoreTxReady(*(undefined1 *)((int)piVar3 + 0x19));
    piVar3 = piVar3 + 7;
  }
  *(undefined1 *)(iVar1 + 0x21) = 1;
  hciCoreResetStart();
  return CONCAT44(uStack_14,uStack_18);
}

