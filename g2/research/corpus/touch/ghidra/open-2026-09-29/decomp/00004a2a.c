
void touch_state_172a_sync_records(int *param_1,int param_2)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  
  bVar1 = *(byte *)(param_1 + 1);
  uVar4 = (uint)bVar1;
  if ((uVar4 != 0) && (uVar4 != 0xff)) {
    uVar5 = *(uint *)(param_2 + 0x70);
    uVar2 = (uint)*(byte *)(*(int **)(param_2 + 0x3c) + 1);
    iVar8 = *param_1;
    iVar7 = **(int **)(param_2 + 0x3c);
    uVar3 = uVar5 >> 8 & 0xff;
    if (uVar2 == 0xff) {
      uVar2 = 0;
    }
    else if (uVar4 < uVar2) {
      uVar2 = uVar4;
    }
    for (uVar6 = 0; uVar6 < uVar2; uVar6 = uVar6 + 1) {
      touch_state_16e6_blend_pair(param_2,iVar8,iVar7);
      iVar8 = iVar8 + 8;
      iVar7 = iVar7 + uVar3 * 8;
    }
    for (; uVar6 < uVar4; uVar6 = uVar6 + 1) {
      touch_state_16d4_copy8(uVar5,iVar8,iVar7);
      iVar8 = iVar8 + 8;
      iVar7 = iVar7 + uVar3 * 8;
    }
  }
  *(byte *)(*(int *)(param_2 + 0x3c) + 4) = bVar1;
  return;
}

