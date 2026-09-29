
void LvpPrintMaxKwsList(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined *puVar3;
  undefined *puVar4;
  undefined *puVar5;
  undefined *puVar6;
  int iVar7;
  uint uVar8;
  
  puVar3 = PTR_s__LVP_MAX_DECODE_Demo_Kws_List__T_102088e4;
  uVar2 = uRam102088e0;
  iVar1 = iRam102088dc;
  iVar7 = 0;
  *(undefined4 *)(iRam102088dc + 0x58) = 2;
  *(undefined4 *)(iVar1 + 0x5c) = uVar2;
  gx8002_printf(puVar3);
  puVar6 = PTR_DAT_102088f4;
  puVar5 = PTR_s_TRH___02d___102088f0;
  puVar4 = PTR_s_KV___02d___102088ec;
  puVar3 = PTR_s__LVP_MAX_DECODE_KWS___s___102088e8;
  for (uVar8 = 0; uVar8 < *(uint *)(iVar1 + 0x58); uVar8 = uVar8 + 1) {
    gx8002_printf(puVar3,*(int *)(iVar1 + 0x5c) + iVar7);
    gx8002_printf(puVar4,*(undefined4 *)(*(int *)(iVar1 + 0x5c) + iVar7 + 0x50));
    gx8002_printf(puVar5,*(undefined4 *)(*(int *)(iVar1 + 0x5c) + iVar7 + 0x4c));
    gx8002_printf(puVar6);
    iVar7 = iVar7 + 0x58;
  }
  return;
}

