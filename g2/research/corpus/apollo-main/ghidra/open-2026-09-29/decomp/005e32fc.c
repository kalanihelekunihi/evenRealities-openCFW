
undefined8 smpiActStkEncrypt(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined1 uVar2;
  int aiStack_20 [4];
  
  if (*(byte *)(param_1 + 0x24) < *(byte *)(param_1 + 0x2b)) {
    bVar1 = *(byte *)(param_1 + 0x24);
  }
  else {
    bVar1 = *(byte *)(param_1 + 0x2b);
  }
  aiStack_20[0] = param_1;
  aiStack_20[1] = param_2;
  aiStack_20[2] = param_3;
  aiStack_20[3] = param_4;
  FUN_00439be4(aiStack_20,*(undefined4 *)(param_2 + 4),bVar1);
  FUN_0043c0e4((uint)bVar1 + (int)aiStack_20,0x10 - (uint)bVar1,0);
  *(undefined1 *)(param_1 + 0x44) = 1;
  if ((int)((uint)*(byte *)(param_1 + 0x40) << 0x1d) < 0) {
    uVar2 = 2;
  }
  else {
    uVar2 = 1;
  }
  DmSmpEncryptReq(*(undefined1 *)(param_1 + 0x3d),uVar2,aiStack_20);
  return CONCAT44(aiStack_20[1],aiStack_20[0]);
}

