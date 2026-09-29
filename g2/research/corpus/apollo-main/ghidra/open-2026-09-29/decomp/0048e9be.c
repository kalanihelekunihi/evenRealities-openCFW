
undefined8 FUN_0048e9be(int param_1,uint param_2,int param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  iVar7 = param_2 * 4 + 8;
  uVar3 = FUN_0047dce4();
  iVar2 = DAT_0048ed78;
  iVar6 = *(int *)(DAT_0048ed78 + 8);
  while (0x1000 < (uint)(iVar7 + (iVar6 - *(int *)(iVar2 + 0xc)))) {
    iVar8 = *(int *)(iVar2 + 0xc);
    iVar4 = FUN_0048e8f0(iVar8);
    iVar4 = iVar4 + iVar8;
    *(int *)(iVar2 + 0xc) = iVar4;
    if (*(int *)(iVar2 + 0x10) - iVar4 < 0) {
      *(int *)(iVar2 + 0x10) = iVar4;
      *(int *)(iVar2 + 0x14) = *(int *)(iVar2 + 0x14) + 1;
    }
  }
  FUN_0048e8d4(iVar6,param_2 & 0xf | 0xa0 | param_1 << 8);
  FUN_0048e8d4(iVar6 + 4,param_4);
  for (uVar5 = 0; uVar5 < param_2; uVar5 = uVar5 + 1) {
    FUN_0048e8d4(iVar6 + uVar5 * 4 + 8,*(undefined4 *)(param_3 + uVar5 * 4));
  }
  *(int *)(iVar2 + 8) = iVar7 + iVar6;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  return CONCAT44(param_1,uVar3);
}

