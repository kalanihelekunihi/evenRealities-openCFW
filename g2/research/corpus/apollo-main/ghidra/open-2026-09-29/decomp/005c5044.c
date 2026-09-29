
void FUN_005c5044(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined1 *puVar7;
  uint uVar8;
  uint uVar9;
  bool bVar10;
  undefined4 local_220;
  uint local_21c;
  uint local_218;
  undefined4 local_214;
  int local_210;
  int local_20c;
  int local_208;
  int local_204;
  int local_200;
  int local_1fc;
  int local_1f8;
  int local_1f4;
  int local_1f0;
  uint local_1ec;
  uint local_1e8;
  int local_1e4;
  int local_1e0;
  undefined1 auStack_1dc [16];
  undefined4 local_1cc;
  undefined4 local_1c0;
  undefined4 local_1ac;
  int local_198;
  int local_194;
  undefined1 auStack_170 [16];
  undefined4 local_160;
  undefined1 *local_154;
  undefined4 local_150;
  undefined4 local_148;
  undefined4 local_144;
  byte local_11d;
  byte local_11c;
  undefined1 auStack_10c [128];
  undefined1 auStack_8c [16];
  undefined4 local_7c;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_64;
  undefined4 local_60;
  byte local_39;
  undefined4 uStack_28;
  
  iVar3 = *param_1;
  uStack_28 = param_4;
  local_214 = FUN_00451960(param_1);
  iVar4 = FUN_005c45ce(iVar3,0);
  iVar5 = FUN_005c45ba(iVar3,0);
  local_210 = FUN_005c45c4(iVar3,0);
  local_210 = iVar4 + local_210;
  FUN_00489f5e(auStack_8c);
  local_7c = local_214;
  FUN_00452988(iVar3,0x20000,auStack_8c);
  if (*(int *)(iVar3 + 0x30) == 0) {
    FUN_005c48d8(iVar3,auStack_10c,0x80);
    puVar7 = auStack_10c;
  }
  else {
    puVar7 = *(undefined1 **)(iVar3 + 0x30);
  }
  bVar10 = (*(byte *)(iVar3 + 0x4c) & 0xf) != 1;
  iVar6 = FUN_005c45ec(iVar3,0);
  if (*(int *)(iVar3 + 0x34) != 0) {
    cVar1 = FUN_00488cb8(*(undefined4 *)(iVar3 + 0x34));
    if (cVar1 == '\x02') {
      local_218 = (uint)(local_39 >> 3);
      local_21c = 0x1fffffff;
      local_220 = local_64;
      FUN_00489546(&local_1ec,*(undefined4 *)(iVar3 + 0x34),local_6c,local_60);
      uVar8 = local_1ec;
      uVar9 = local_1e8;
    }
    else {
      cVar2 = FUN_00488f6a(*(undefined4 *)(iVar3 + 0x34),&local_220);
      if (cVar2 == '\x01') {
        uVar8 = local_21c & 0xffff;
        uVar9 = local_21c >> 0x10;
      }
      else {
        uVar9 = 0xffffffff;
        uVar8 = 0xffffffff;
      }
    }
    local_1f8 = *(int *)(iVar3 + 0x18);
    local_1f0 = uVar9 + local_1f8 + -1;
    local_1fc = *(int *)(iVar3 + 0x14);
    local_1f4 = uVar8 + local_1fc + -1;
    if (iVar6 != 1 && bVar10) {
      local_220 = 0;
      FUN_00451082(iVar3 + 0x14,&local_1fc,8,-local_210);
    }
    else {
      local_220 = 0;
      FUN_00451082(iVar3 + 0x14,&local_1fc,7,iVar4 + iVar5);
    }
    if (cVar1 == '\x02') {
      local_70 = *(undefined4 *)(iVar3 + 0x34);
      FUN_00489fe0(local_214,auStack_8c,&local_1fc);
    }
    else {
      FUN_00488918(auStack_1dc);
      local_1cc = local_214;
      FUN_00452a34(iVar3,0x20000,auStack_1dc);
      local_194 = (int)uVar9 / 2;
      local_198 = (int)uVar8 / 2;
      local_1ac = FUN_005c459c(iVar3,0x20000);
      local_1c0 = *(undefined4 *)(iVar3 + 0x34);
      FUN_00488a38(local_214,auStack_1dc,&local_1fc);
    }
  }
  FUN_00489f5e(auStack_170);
  local_160 = local_214;
  FUN_00452988(iVar3,0,auStack_170);
  local_218 = (uint)(local_11d >> 3);
  local_21c = 0x1fffffff;
  local_220 = local_148;
  FUN_00489546(&local_1e4,puVar7,local_150,local_144);
  local_20c = *(int *)(iVar3 + 0x14);
  local_204 = local_1e4 + local_20c + -1;
  local_208 = *(int *)(iVar3 + 0x18);
  local_200 = local_1e0 + local_208 + -1;
  if (*(int *)(iVar3 + 0x34) == 0) {
    local_220 = 0;
    FUN_00451082(iVar3 + 0x14,&local_20c,9,0);
  }
  else if (iVar6 != 1 && bVar10) {
    local_220 = 0;
    FUN_00451082(iVar3 + 0x14,&local_20c,7,iVar4 + iVar5);
  }
  else {
    local_220 = 0;
    FUN_00451082(iVar3 + 0x14,&local_20c,8,-local_210);
  }
  if (*(int *)(iVar3 + 0x30) == 0) {
    local_11c = local_11c | 1;
  }
  local_154 = puVar7;
  FUN_00489fe0(local_214,auStack_170,&local_20c);
  return;
}

