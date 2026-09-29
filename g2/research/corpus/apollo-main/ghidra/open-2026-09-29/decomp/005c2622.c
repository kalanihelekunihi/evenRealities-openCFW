
uint FUN_005c2622(int param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int local_50;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_2c;
  int local_28;
  
  FUN_0043fc2a(param_1,&local_3c);
  local_28 = FUN_0043fd9e(param_1);
  local_2c = FUN_0043fdda(param_1);
  iVar1 = FUN_005c161a(param_1,0);
  iVar2 = FUN_005c1624(param_1,0);
  iVar3 = FUN_005c1606(param_1,0);
  iVar4 = FUN_005c1610(param_1,0);
  uVar5 = FUN_005c162e(param_1,0);
  uVar6 = FUN_005c1638(param_1,0);
  local_40 = (uVar5 & 1) + (int)uVar5 / 2 + 1;
  iVar7 = (uVar6 & 1) + (int)uVar6 / 2 + 1;
  if (0xc < local_40) {
    local_40 = 0xd;
  }
  if (0xc < iVar7) {
    iVar7 = 0xd;
  }
  if (0xc < iVar2) {
    iVar2 = 0xd;
  }
  if (0xc < iVar3) {
    iVar3 = 0xd;
  }
  if (0xc < iVar4) {
    iVar4 = 0xd;
  }
  for (uVar5 = 0; uVar5 < *(uint *)(param_1 + 0x38); uVar5 = uVar5 + 1) {
    FUN_005c15e8(&local_50,uVar5 * 0x10 + *(int *)(param_1 + 0x30));
    if (iVar1 < local_50) {
      local_50 = (local_3c + local_50) - iVar7;
    }
    else {
      iVar8 = iVar1;
      if (0xc < iVar1) {
        iVar8 = 0xd;
      }
      local_50 = (local_3c + local_50) - iVar8;
    }
    if (iVar3 < local_4c) {
      local_4c = (local_38 + local_4c) - local_40;
    }
    else {
      iVar8 = iVar3;
      if (0xc < iVar3) {
        iVar8 = 0xd;
      }
      local_4c = (local_38 + local_4c) - iVar8;
    }
    if (local_48 < (local_28 - iVar2) + -2) {
      local_48 = iVar7 + local_3c + local_48;
    }
    else {
      iVar8 = iVar2;
      if (0xc < iVar2) {
        iVar8 = 0xd;
      }
      local_48 = iVar8 + local_3c + local_48;
    }
    if (local_44 < (local_2c - iVar4) + -2) {
      local_44 = local_40 + local_38 + local_44;
    }
    else {
      iVar8 = iVar4;
      if (0xc < iVar4) {
        iVar8 = 0xd;
      }
      local_44 = iVar8 + local_38 + local_44;
    }
    iVar8 = FUN_00450dd4(&local_50,param_2,0);
    if (iVar8 != 0) break;
  }
  if (uVar5 == *(uint *)(param_1 + 0x38)) {
    uVar5 = 0xffff;
  }
  return uVar5;
}

