
void smpiActPairReq(int param_1,int param_2)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  
  DmConnSetIdle(*(undefined1 *)(param_1 + 0x3d),1,1);
  *(undefined1 *)(param_1 + 0x3f) = 2;
  smpStartRspTimer(param_1);
  uVar2 = WsfBufAlloc(0x40);
  *(undefined4 *)(param_1 + 0x30) = uVar2;
  iVar3 = smpMsgAlloc(0xf);
  if (iVar3 != 0) {
    *(undefined1 *)(iVar3 + 8) = 1;
    piVar1 = DAT_005e3404;
    *(undefined1 *)(iVar3 + 9) = *(undefined1 *)(*DAT_005e3404 + 4);
    *(undefined1 *)(iVar3 + 10) = *(undefined1 *)(param_2 + 4);
    *(undefined1 *)(iVar3 + 0xb) = *(undefined1 *)(param_2 + 5);
    *(undefined1 *)(iVar3 + 0xc) = *(undefined1 *)(*piVar1 + 6);
    *(undefined1 *)(iVar3 + 0xd) = *(undefined1 *)(param_2 + 6);
    *(undefined1 *)(iVar3 + 0xe) = *(undefined1 *)(param_2 + 7);
    FUN_00439be4(param_1 + 0x20,iVar3 + 8,7);
    smpSendPkt(param_1,iVar3);
  }
  return;
}

