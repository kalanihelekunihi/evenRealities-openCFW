
void smpCalcC1Part1(int param_1,undefined4 param_2,byte *param_3)

{
  byte bVar1;
  undefined1 uVar2;
  int iVar3;
  byte *pbVar4;
  undefined4 local_28;
  byte local_24;
  byte local_23;
  byte local_22 [14];
  
  if (*(char *)(param_1 + 0x3a) == '\0') {
    DmConnPeerRpa(*(undefined1 *)(param_1 + 0x3d));
    iVar3 = FUN_004d2974();
    if (iVar3 == 0) {
      bVar1 = 1;
    }
    else {
      bVar1 = DmConnPeerAddrType(*(undefined1 *)(param_1 + 0x3d));
    }
    DmConnLocalRpa(*(undefined1 *)(param_1 + 0x3d));
    iVar3 = FUN_004d2974();
    if (iVar3 == 0) {
      local_23 = 1;
    }
    else {
      local_23 = DmConnLocalAddrType(*(undefined1 *)(param_1 + 0x3d));
    }
  }
  else {
    DmConnLocalRpa(*(undefined1 *)(param_1 + 0x3d));
    iVar3 = FUN_004d2974();
    if (iVar3 == 0) {
      bVar1 = 1;
    }
    else {
      bVar1 = DmConnLocalAddrType(*(undefined1 *)(param_1 + 0x3d));
    }
    DmConnPeerRpa(*(undefined1 *)(param_1 + 0x3d));
    iVar3 = FUN_004d2974();
    if (iVar3 == 0) {
      local_23 = 1;
    }
    else {
      local_23 = DmConnPeerAddrType(*(undefined1 *)(param_1 + 0x3d));
    }
  }
  local_24 = bVar1 ^ *param_3;
  local_23 = local_23 ^ param_3[1];
  param_3 = param_3 + 2;
  pbVar4 = local_22;
  for (bVar1 = 0; bVar1 < 7; bVar1 = bVar1 + 1) {
    *pbVar4 = *(byte *)((uint)bVar1 + param_1 + 0x20) ^ *param_3;
    param_3 = param_3 + 1;
    pbVar4 = pbVar4 + 1;
  }
  for (bVar1 = 0; bVar1 < 7; bVar1 = bVar1 + 1) {
    *pbVar4 = *(byte *)((uint)bVar1 + param_1 + 0x27) ^ *param_3;
    param_3 = param_3 + 1;
    pbVar4 = pbVar4 + 1;
  }
  local_28 = 0xb;
  uVar2 = FUN_00536426(param_2,&local_24,*(undefined1 *)(DAT_00537ebc + 0xec),
                       *(undefined1 *)(param_1 + 0x3d));
  *(undefined1 *)(param_1 + 0x41) = uVar2;
  if (*(char *)(param_1 + 0x41) == -1) {
    local_28 = CONCAT13(8,CONCAT12(3,(undefined2)local_28));
    smpSmExecute(param_1,&local_28);
  }
  return;
}

