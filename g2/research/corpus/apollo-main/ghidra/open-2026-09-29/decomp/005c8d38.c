
void FUN_005c8d38(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  char *pcVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int local_98;
  int local_94;
  int local_90;
  int local_8c;
  undefined1 auStack_88 [16];
  undefined4 local_78;
  undefined4 local_6c;
  byte local_35;
  
  iVar1 = *param_1;
  uVar2 = FUN_00451960(param_1);
  pcVar3 = (char *)FUN_004997f8(*(undefined4 *)(iVar1 + 0x2c));
  if (((*pcVar3 == '\0') && (*(int *)(iVar1 + 0x30) != 0)) && (**(char **)(iVar1 + 0x30) != '\0')) {
    FUN_00489f5e(auStack_88);
    local_78 = uVar2;
    FUN_00452988(iVar1,0x80000,auStack_88);
    if ((*(byte *)(iVar1 + 0x70) & 0xf) >> 3 != 0) {
      local_35 = local_35 | 8;
    }
    iVar4 = FUN_005c78ca(iVar1,0);
    iVar5 = FUN_005c78d4(iVar1,0);
    iVar6 = FUN_005c78b6(iVar1,0);
    iVar7 = FUN_005c78c0(iVar1,0);
    iVar8 = FUN_005c78de(iVar1,0);
    FUN_005c78a4(&local_98,iVar1 + 0x14);
    local_98 = iVar8 + iVar4 + local_98;
    local_90 = (local_90 - iVar5) - iVar8;
    local_94 = iVar8 + iVar6 + local_94;
    local_8c = (local_8c - iVar7) - iVar8;
    local_6c = *(undefined4 *)(iVar1 + 0x30);
    FUN_00489fe0(uVar2,auStack_88,&local_98);
  }
  return;
}

