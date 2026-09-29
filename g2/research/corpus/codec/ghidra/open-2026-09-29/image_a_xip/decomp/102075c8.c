
undefined4 gx8002_audio_input_env_noise(int param_1)

{
  int iVar1;
  uint uVar2;
  byte bVar3;
  int iVar4;
  undefined4 uVar5;
  
  uVar2 = gx8002_distance_noise();
  iVar1 = iRam10207640;
  if (uVar2 < 0x3f00001) {
    if (uVar2 < 0x600001) {
      iVar4 = *(int *)(iRam10207640 + 0x14) + 1;
      *(int *)(iRam10207640 + 0x14) = iVar4;
      if (iVar4 < 0x97) goto LAB_10207632;
      uVar5 = 0;
      *(undefined4 *)(iVar1 + 0xc) = 0;
      *(undefined4 *)(iVar1 + 0x14) = 0;
      bVar3 = *(byte *)(param_1 + 0xe);
    }
    else {
      iVar4 = *(int *)(iRam10207640 + 0x10) + 1;
      *(int *)(iRam10207640 + 0x10) = iVar4;
      if (iVar4 < 0x33) {
LAB_10207632:
        *(byte *)(param_1 + 0xe) =
             *(byte *)(param_1 + 0xe) & 0xf8 | (byte)*(undefined4 *)(iVar1 + 0x18) & 7;
        return 0;
      }
      *(undefined4 *)(iVar1 + 0xc) = 0;
      *(undefined4 *)(iVar1 + 0x14) = 0;
      bVar3 = *(byte *)(param_1 + 0xe);
      uVar5 = 1;
    }
  }
  else {
    iVar4 = *(int *)(iRam10207640 + 0xc) + 1;
    *(int *)(iRam10207640 + 0xc) = iVar4;
    if (iVar4 < 0x97) goto LAB_10207632;
    *(undefined4 *)(iVar1 + 0x10) = 0;
    *(undefined4 *)(iVar1 + 0x14) = 0;
    bVar3 = *(byte *)(param_1 + 0xe);
    uVar5 = 2;
  }
  *(byte *)(param_1 + 0xe) = bVar3 & 0xf8 | (byte)uVar5;
  *(undefined4 *)(iVar1 + 0x18) = uVar5;
  return 0;
}

