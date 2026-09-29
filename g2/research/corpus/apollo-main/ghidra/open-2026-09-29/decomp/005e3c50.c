
undefined4 smprActSetupKeyDist(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  
  *(undefined1 *)(param_1 + 0x3f) = 0;
  smpStartRspTimer(param_1);
  **(ushort **)(param_1 + 0x30) = (ushort)*(byte *)(param_1 + 0x3d);
  if ((int)((uint)*(byte *)(param_1 + 0x40) << 0x1d) < 0) {
    uVar1 = 2;
  }
  else {
    uVar1 = 1;
  }
  *(undefined1 *)(*(int *)(param_1 + 0x30) + 0x1f) = uVar1;
  if (*(byte *)(param_1 + 0x24) < *(byte *)(param_1 + 0x2b)) {
    uVar1 = *(undefined1 *)(param_1 + 0x24);
  }
  else {
    uVar1 = *(undefined1 *)(param_1 + 0x2b);
  }
  *(undefined1 *)(*(int *)(param_1 + 0x30) + 0x20) = uVar1;
  smprActSendKey(param_1,param_2);
  return param_4;
}

