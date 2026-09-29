
void FUN_005d3c0a(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4,
                 undefined4 param_5,char param_6)

{
  int iVar1;
  int iVar2;
  byte *pbVar3;
  undefined1 *puVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  undefined4 local_d0;
  int local_cc;
  undefined4 local_c8;
  uint local_c4;
  int local_c0;
  undefined1 auStack_bc [20];
  undefined1 auStack_a8 [20];
  undefined1 auStack_94 [20];
  undefined1 auStack_80 [20];
  undefined1 auStack_6c [20];
  undefined1 auStack_58 [20];
  undefined1 auStack_44 [28];
  undefined4 *puStack_28;
  
  iVar5 = *param_1;
  puStack_28 = param_4;
  if ((param_6 == '\0') && (iVar1 = FUN_005d36ea(param_1[1]), iVar1 == 0)) {
    FUN_005d4afe(auStack_44,*param_4);
    local_cc = 1;
    local_d0 = param_5;
    FUN_005d3c0a(param_1[1],param_2,param_3,auStack_44);
  }
  iVar1 = FUN_005d4b14(param_4);
  if (iVar1 == 0) {
    iVar1 = FUN_005d23b2(param_2);
    iVar2 = FUN_005d23b2(param_3);
    FUN_005d4b78(param_4,iVar2 + iVar1);
    iVar1 = FUN_005d4b14(param_4);
    if (iVar1 == 0) {
      if (*(char *)(iVar5 + 8) == '\0') {
        return;
      }
      *(undefined4 *)*param_4 = 0;
      *(undefined1 *)((int)param_1 + 0xd) = 0;
      return;
    }
  }
  param_1[5] = 0;
  param_1[6] = 0;
  FUN_00439c04(auStack_44,param_4,0x1c);
  pbVar3 = (byte *)FUN_005d4b20(auStack_44);
  local_c4 = FUN_005d23b2(param_2);
  if (local_c4 <= (uint)param_4[2]) {
    if (*(char *)(iVar5 + 0xf9) != '\0') {
      FUN_005d3634(auStack_58);
      FUN_005d3a2a(param_1,iVar5 + 0x120,auStack_58);
      FUN_005d3a2a(param_1,auStack_58,iVar5 + 0x10c);
    }
    uVar7 = 0x80;
    for (uVar6 = 0; uVar6 < local_c4; uVar6 = uVar6 + 1) {
      if ((uVar7 & *pbVar3) != 0) {
        local_c8 = 1;
        local_cc = param_1[4];
        local_d0 = param_5;
        FUN_005d3544(auStack_a8,param_2,uVar6,iVar5);
        local_c8 = 0;
        local_cc = param_1[4];
        local_d0 = param_5;
        FUN_005d3544(auStack_bc,param_2,uVar6,iVar5);
        iVar1 = FUN_005d3696(auStack_a8);
        if (((iVar1 != 0) || (iVar1 = FUN_005d3696(auStack_bc), iVar1 != 0)) ||
           (iVar1 = FUN_005d2828(iVar5 + 0xf0,auStack_a8,auStack_bc), iVar1 != 0)) {
          FUN_005d3a2a(param_1,auStack_a8,auStack_bc);
          *pbVar3 = *pbVar3 & ~(byte)uVar7;
        }
      }
      if ((uVar6 & 7) == 7) {
        pbVar3 = pbVar3 + 1;
        uVar7 = 0x80;
      }
      else {
        uVar7 = uVar7 >> 1;
      }
    }
    if (param_6 == '\0') {
      pbVar3 = (byte *)FUN_005d4b20(auStack_44);
      uVar7 = 0x80;
      for (uVar6 = 0; uVar6 < local_c4; uVar6 = uVar6 + 1) {
        if ((uVar7 & *pbVar3) != 0) {
          local_c8 = 1;
          local_cc = param_1[4];
          local_d0 = param_5;
          FUN_005d3544(auStack_80,param_2,uVar6,iVar5);
          local_c8 = 0;
          local_cc = param_1[4];
          local_d0 = param_5;
          FUN_005d3544(auStack_94,param_2,uVar6,iVar5);
          FUN_005d3a2a(param_1,auStack_80,auStack_94);
        }
        if ((uVar6 & 7) == 7) {
          pbVar3 = pbVar3 + 1;
          uVar7 = 0x80;
        }
        else {
          uVar7 = uVar7 >> 1;
        }
      }
    }
    else if (((param_1[5] == 0) || (0 < param_1[9])) || (param_1[param_1[5] * 5 + 4] < 0)) {
      FUN_005d3634(&local_d0);
      local_d0 = 0x31;
      local_c0 = param_1[4];
      FUN_005d3634(auStack_6c);
      FUN_005d3a2a(param_1,&local_d0,auStack_6c);
    }
    FUN_005d36ee(param_1);
    FUN_005d377c(param_1);
    FUN_005d36ee(param_1);
    if (param_6 == '\0') {
      for (uVar6 = 0; uVar6 < (uint)param_1[5]; uVar6 = uVar6 + 1) {
        iVar5 = FUN_005d36a2(param_1 + uVar6 * 5 + 7);
        if (iVar5 == 0) {
          puVar4 = (undefined1 *)FUN_005d23ba(param_2,param_1[uVar6 * 5 + 8]);
          iVar5 = FUN_005d3672(param_1 + uVar6 * 5 + 7);
          if (iVar5 == 0) {
            *(int *)(puVar4 + 0xc) = param_1[uVar6 * 5 + 10];
          }
          else {
            *(int *)(puVar4 + 0x10) = param_1[uVar6 * 5 + 10];
          }
          *puVar4 = 1;
        }
      }
    }
    *(undefined1 *)(param_1 + 3) = 1;
    FUN_005d4b1c(param_4,0);
  }
  return;
}

