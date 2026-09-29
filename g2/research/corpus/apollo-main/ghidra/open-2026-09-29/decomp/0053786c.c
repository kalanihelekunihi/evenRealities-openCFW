
void smpCalcC1Part2(int param_1,undefined4 param_2,byte *param_3,undefined4 param_4)

{
  undefined1 uVar1;
  byte *pbVar2;
  int iVar3;
  byte *pbVar4;
  byte *pbVar5;
  char cVar6;
  undefined4 local_30;
  byte local_2c [16];
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  if (*(char *)(param_1 + 0x3a) == '\0') {
    pbVar2 = (byte *)DmConnPeerRpa(*(undefined1 *)(param_1 + 0x3d));
    iVar3 = FUN_004d2974(pbVar2);
    if (iVar3 != 0) {
      pbVar2 = (byte *)DmConnPeerAddr(*(undefined1 *)(param_1 + 0x3d));
    }
    pbVar4 = (byte *)DmConnLocalRpa(*(undefined1 *)(param_1 + 0x3d));
    iVar3 = FUN_004d2974(pbVar4);
    if (iVar3 != 0) {
      pbVar4 = (byte *)DmConnLocalAddr(*(undefined1 *)(param_1 + 0x3d));
    }
  }
  else {
    pbVar2 = (byte *)DmConnLocalRpa(*(undefined1 *)(param_1 + 0x3d));
    iVar3 = FUN_004d2974(pbVar2);
    if (iVar3 != 0) {
      pbVar2 = (byte *)DmConnLocalAddr(*(undefined1 *)(param_1 + 0x3d));
    }
    pbVar4 = (byte *)DmConnPeerRpa(*(undefined1 *)(param_1 + 0x3d));
    iVar3 = FUN_004d2974(pbVar4);
    if (iVar3 != 0) {
      pbVar4 = (byte *)DmConnPeerAddr(*(undefined1 *)(param_1 + 0x3d));
    }
  }
  pbVar5 = local_2c;
  for (cVar6 = '\x06'; cVar6 != '\0'; cVar6 = cVar6 + -1) {
    *pbVar5 = *pbVar4 ^ *param_3;
    param_3 = param_3 + 1;
    pbVar4 = pbVar4 + 1;
    pbVar5 = pbVar5 + 1;
  }
  for (cVar6 = '\x06'; cVar6 != '\0'; cVar6 = cVar6 + -1) {
    *pbVar5 = *pbVar2 ^ *param_3;
    param_3 = param_3 + 1;
    pbVar2 = pbVar2 + 1;
    pbVar5 = pbVar5 + 1;
  }
  *pbVar5 = *param_3;
  pbVar5[1] = param_3[1];
  pbVar5[2] = param_3[2];
  pbVar5[3] = param_3[3];
  local_30 = 0xb;
  uVar1 = FUN_00536426(param_2,local_2c,*(undefined1 *)(DAT_00537ebc + 0xec),
                       *(undefined1 *)(param_1 + 0x3d));
  *(undefined1 *)(param_1 + 0x41) = uVar1;
  if (*(char *)(param_1 + 0x41) == -1) {
    local_30 = CONCAT13(8,CONCAT12(3,(undefined2)local_30));
    smpSmExecute(param_1,&local_30);
  }
  return;
}

