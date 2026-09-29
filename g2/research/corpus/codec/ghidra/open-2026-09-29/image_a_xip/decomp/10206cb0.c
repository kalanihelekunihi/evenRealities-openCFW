
void gx8002_kws_flash_load(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined *puVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  undefined1 auStack_3c [4];
  undefined4 uStack_38;
  int iStack_34;
  int iStack_28;
  int iStack_24;
  int iStack_20;
  
  iVar1 = LvpModelGetCmdSize();
  iVar2 = LvpModelGetWeightSize();
  uStack_38 = 0x20000000;
  iVar3 = LvpModelGetOpsSize();
  uVar6 = iVar3 + 3;
  if ((int)uVar6 < 0) {
    uVar6 = iVar3 + 6;
  }
  iVar7 = (uVar6 & 0xfffffffc) + 0x20000000;
  iStack_34 = iVar7;
  iVar3 = LvpModelGetDataSize();
  uVar6 = iVar3 + 3;
  if ((int)uVar6 < 0) {
    uVar6 = iVar3 + 6;
  }
  iVar7 = iVar7 + (uVar6 & 0xfffffffc);
  iStack_24 = iVar7;
  iVar3 = LvpModelGetTmpSize();
  uVar6 = iVar3 + 3;
  if ((int)uVar6 < 0) {
    uVar6 = iVar3 + 6;
  }
  iStack_28 = (uVar6 & 0xfffffffc) + iVar7;
  uVar6 = iVar1 + 3U & 0xfffffffc;
  iStack_20 = iStack_28 + uVar6;
  iVar3 = func_0x10025930();
  iVar7 = func_0x1002475c(0,0,0x5dc000,0x800);
  iVar1 = DAT_10206d84;
  puVar4 = PTR_s__LVP_KWS__Init_Flash_Failed_10206d80;
  if (iVar7 != 0) {
    iVar5 = func_0x100247b8(iVar7,DAT_10206d84,iStack_28,uVar6);
    iVar1 = func_0x100247b8(iVar7,uVar6 + iVar1,iStack_20,iVar2 + 3U & 0xfffffffc);
    iVar2 = func_0x10025930();
    gx8002_printf(PTR_s__LVP_KWS__Kws_Use__d_ms_10206d88,iVar2 - iVar3);
    puVar4 = PTR_s__LVP_KWS__Read_Flash_Failed_10206d8c;
    if (iVar5 == 0 && iVar1 == 0) {
      LvpSetSnpuTask(auStack_3c);
      return;
    }
  }
  gx8002_printf(puVar4);
  return;
}

