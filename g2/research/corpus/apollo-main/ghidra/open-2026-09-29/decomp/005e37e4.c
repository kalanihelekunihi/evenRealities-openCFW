
void smpiScActDHKeyCheckVerify(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined1 uVar2;
  int iVar3;
  ushort uStack_28;
  undefined1 uStack_26;
  undefined1 uStack_25;
  undefined1 auStack_24 [16];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  iVar3 = FUN_004751c8(*(int *)(param_2 + 4) + 9,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,
                       0x10);
  if (iVar3 == 0) {
    if (*(byte *)(param_1 + 0x24) < *(byte *)(param_1 + 0x2b)) {
      bVar1 = *(byte *)(param_1 + 0x24);
    }
    else {
      bVar1 = *(byte *)(param_1 + 0x2b);
    }
    FUN_00439be4(auStack_24,*(int *)(*(int *)(param_1 + 0x48) + 0x18) + 0x10,bVar1);
    FUN_0043c0e4(auStack_24 + bVar1,0x10 - (uint)bVar1,0);
    *(undefined1 *)(param_1 + 0x44) = 1;
    uVar2 = smpGetScSecLevel(param_1);
    DmSmpEncryptReq(*(undefined1 *)(param_1 + 0x3d),uVar2,auStack_24);
  }
  else {
    uStack_28 = (ushort)*(byte *)(param_1 + 0x3d);
    uStack_25 = 0xb;
    *(char *)(param_1 + 0x42) = *(char *)(param_1 + 0x42) + '\x01';
    SmpDbPairingFailed(*(undefined1 *)(param_1 + 0x3d));
    if (*(char *)(param_1 + 0x42) == *(char *)(*DAT_005e38c4 + 7)) {
      uStack_26 = 0xd;
    }
    else {
      uStack_26 = 0x1d;
    }
    smpSmExecute(param_1,&uStack_28);
  }
  return;
}

