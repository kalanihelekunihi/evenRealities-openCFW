
undefined8 smprScActDHKeyCheckSend(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  ushort uStack_18;
  undefined1 uStack_16;
  undefined1 uStack_15;
  undefined4 uStack_14;
  
  uStack_18 = (ushort)param_3;
  uStack_16 = (undefined1)((uint)param_3 >> 0x10);
  uStack_15 = (undefined1)((uint)param_3 >> 0x18);
  uStack_14 = param_4;
  smpLogByteArray(PTR_s_DHKey_Eb_005e4220,*(undefined4 *)(param_2 + 4),0x10);
  FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,*(undefined4 *)(param_2 + 4));
  iVar2 = FUN_004751c8(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x50,
                       *(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),0x10);
  if (iVar2 == 0) {
    if (*(byte *)(param_1 + 0x24) < *(byte *)(param_1 + 0x2b)) {
      bVar1 = *(byte *)(param_1 + 0x24);
    }
    else {
      bVar1 = *(byte *)(param_1 + 0x2b);
    }
    FUN_0043c0e4((uint)bVar1 + *(int *)(*(int *)(param_1 + 0x48) + 0x18) + 0x10,0x10 - (uint)bVar1,0
                );
    *(undefined1 *)(param_1 + 0x44) = 1;
    smpScSendDHKeyCheck(param_1,param_2,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10);
  }
  else {
    uStack_18 = (ushort)*(byte *)(param_1 + 0x3d);
    uStack_15 = 0xb;
    *(char *)(param_1 + 0x42) = *(char *)(param_1 + 0x42) + '\x01';
    SmpDbPairingFailed(*(undefined1 *)(param_1 + 0x3d));
    if (*(char *)(param_1 + 0x42) == *(char *)(*DAT_005e4224 + 7)) {
      uStack_16 = 0xd;
    }
    else {
      uStack_16 = 0x1d;
    }
    smpSmExecute(param_1,&uStack_18);
  }
  return CONCAT44(uStack_14,CONCAT13(uStack_15,CONCAT12(uStack_16,uStack_18)));
}

