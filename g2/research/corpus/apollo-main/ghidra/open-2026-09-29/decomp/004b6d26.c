
void DmConnUpdate(byte param_1,undefined4 param_2)

{
  undefined1 uVar1;
  ushort *puVar2;
  int iVar3;
  
  puVar2 = (ushort *)WsfMsgAlloc(0x24);
  if (puVar2 != (ushort *)0x0) {
    iVar3 = DmConnRole(param_1);
    if (iVar3 == 0) {
      uVar1 = 0x70;
    }
    else {
      uVar1 = 0x71;
    }
    *(undefined1 *)(puVar2 + 1) = uVar1;
    *puVar2 = (ushort)param_1;
    FUN_00439be4(puVar2 + 2,param_2,0xc);
    WsfMsgSend(*(undefined1 *)(DAT_004b6f20 + 0xc),puVar2);
  }
  return;
}

