
undefined4 attcProcMtuRsp(undefined4 *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  ushort uVar1;
  short sVar2;
  uint uVar3;
  
  uVar3 = (uint)*(byte *)(param_3 + 10) * 0x100 + (uint)*(byte *)(param_3 + 9);
  if (uVar3 < 0xf7) {
    uVar3 = 0xf7;
  }
  uVar1 = HciGetMaxRxAclLen();
  if ((int)(uint)*(ushort *)(*DAT_004b5998 + 4) < (int)(uVar1 - 4)) {
    sVar2 = *(short *)(*DAT_004b5998 + 4);
  }
  else {
    sVar2 = HciGetMaxRxAclLen();
    sVar2 = sVar2 + -4;
  }
  attSetMtu(*param_1,*(undefined1 *)(param_1 + 10),uVar3,sVar2);
  return param_4;
}

