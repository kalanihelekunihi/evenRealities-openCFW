
uint touch_application_2638_dispatch(int param_1,int param_2)

{
  ushort uVar1;
  bool bVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 *puVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  
  puVar6 = (undefined4 *)(*(int *)(param_2 + 0xc) + param_1 * 0x90);
  uVar1 = *(ushort *)(puVar6 + 0x1d);
  iVar7 = 0;
  uVar10 = 0;
  bVar2 = false;
  while (!bVar2) {
    iVar5 = puVar6[1];
    iVar3 = puVar6[5];
    iVar8 = puVar6[7];
    if ((*(ushort *)(puVar6 + 0x1d) & 0x300) == 0x200) {
      iVar7 = puVar6[8];
    }
    for (uVar9 = 0; uVar9 < *(ushort *)(puVar6 + 0xe); uVar9 = uVar9 + 1) {
      touch_pipeline_1da0_filter_chain(puVar6,iVar5,iVar8,iVar7);
      uVar4 = touch_pipeline_1cee_update(*puVar6,iVar5,iVar3,param_2);
      uVar10 = uVar10 | uVar4;
      touch_record_2620_threshold_delta(*puVar6,iVar5);
      iVar5 = iVar5 + 10;
      iVar3 = iVar3 + 2;
      iVar8 = iVar8 + (uVar1 & 0xf) * 2;
      if (iVar7 != 0) {
        iVar7 = iVar7 + 1;
      }
    }
    bVar2 = true;
  }
  return uVar10;
}

