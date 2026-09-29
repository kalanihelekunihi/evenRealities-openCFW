
uint smprActSendPairRsp(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 uStack_18;
  
  *(undefined1 *)(param_1 + 0x27) = 2;
  piVar1 = DAT_005e3d44;
  *(undefined1 *)(param_1 + 0x28) = *(undefined1 *)(*DAT_005e3d44 + 4);
  *(undefined1 *)(param_1 + 0x29) = *(undefined1 *)(param_2 + 4);
  *(undefined1 *)(param_1 + 0x2a) = *(undefined1 *)(param_2 + 5);
  *(undefined1 *)(param_1 + 0x2b) = *(undefined1 *)(*piVar1 + 6);
  *(undefined1 *)(param_1 + 0x2c) = *(undefined1 *)(param_2 + 6);
  *(undefined1 *)(param_1 + 0x2d) = *(undefined1 *)(param_2 + 7);
  iVar2 = DAT_005e3d48;
  uStack_18 = param_4;
  iVar3 = (**(code **)(DAT_005e3d48 + 0xf0))(param_1,(int)&uStack_18 + 1,&uStack_18);
  if (iVar3 != 0) {
    if ((int)((uint)(*(byte *)(param_1 + 0x23) & *(byte *)(param_2 + 5)) << 0x1c) < 0) {
      *(undefined1 *)(param_1 + 0x3f) = 0xc;
    }
    else {
      *(undefined1 *)(param_1 + 0x3f) = 3;
    }
    smpStartRspTimer(param_1);
    iVar3 = smpMsgAlloc(0xf);
    if (iVar3 != 0) {
      FUN_00439be4(iVar3 + 8,param_1 + 0x27,7);
      smpSendPkt(param_1,iVar3);
    }
    (**(code **)(iVar2 + 0xf4))(param_1,uStack_18._1_1_,uStack_18 & 0xff);
  }
  return uStack_18;
}

