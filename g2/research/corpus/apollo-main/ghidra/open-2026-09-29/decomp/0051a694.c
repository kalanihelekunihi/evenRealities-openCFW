
int FUN_0051a694(float param_1,float param_2,float param_3,float param_4,float param_5,float param_6
                ,undefined4 param_7,int param_8,int param_9)

{
  int iVar1;
  int iVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  undefined1 auStack_78 [12];
  float local_6c;
  float local_68;
  float local_64;
  float local_60;
  float local_5c;
  float local_58;
  float local_54;
  float local_50;
  
  param_1 = param_1 * DAT_0051a8d8;
  fVar7 = param_2 * DAT_0051a8d8 - param_1;
  fVar3 = (float)FUN_00563f40(fVar7 * 0.25);
  fVar3 = fVar3 * DAT_0051a8dc;
  fVar4 = (float)FUN_0050968c(fVar7);
  local_60 = (float)FUN_00509690(fVar7);
  local_6c = 1.0;
  local_5c = 1.0;
  local_54 = fVar4 + fVar3 * local_60;
  local_50 = local_60 - fVar3 * fVar4;
  local_68 = 0.0;
  fVar8 = (*(float *)(param_8 + 0x24) / DAT_0051a8e0) * DAT_0051a8e4;
  local_64 = fVar4;
  local_58 = fVar3;
  fVar3 = (float)FUN_0050968c(param_1);
  fVar4 = (float)FUN_00509690(param_1);
  fVar7 = (float)FUN_0050968c(fVar8);
  fVar8 = (float)FUN_00509690(fVar8);
  if (param_9 << 0x1f < 0) {
    local_6c = *(float *)(param_8 + 0xc);
    local_68 = *(float *)(param_8 + 0x10);
  }
  else {
    fVar5 = (fVar4 + fVar3 * DAT_0051a8e8) * param_6;
    fVar6 = (fVar3 - fVar4 * DAT_0051a8e8) * param_5;
    local_68 = fVar6 * fVar8 + fVar5 * fVar7 + param_4;
    local_6c = (fVar6 * fVar7 - fVar5 * fVar8) + param_3;
  }
  fVar5 = (fVar4 + local_58 * fVar3) * param_6;
  fVar6 = (fVar3 - local_58 * fVar4) * param_5;
  local_58 = fVar6 * fVar8 + fVar5 * fVar7 + param_4;
  local_5c = (fVar6 * fVar7 - fVar5 * fVar8) + param_3;
  fVar5 = (local_54 * fVar4 + local_50 * fVar3) * param_6;
  fVar6 = (local_54 * fVar3 - local_50 * fVar4) * param_5;
  local_50 = fVar6 * fVar8 + fVar5 * fVar7 + param_4;
  local_54 = (fVar6 * fVar7 - fVar5 * fVar8) + param_3;
  if (param_9 << 0x1e < 0) {
    local_64 = *(float *)(param_8 + 0x14);
    local_60 = *(float *)(param_8 + 0x18);
  }
  else {
    param_6 = (local_64 * fVar4 + local_60 * fVar3) * param_6;
    param_5 = (local_64 * fVar3 - local_60 * fVar4) * param_5;
    local_60 = param_5 * fVar8 + param_6 * fVar7 + param_4;
    local_64 = (param_5 * fVar7 - param_6 * fVar8) + param_3;
  }
  iVar1 = FUN_00516cf8(auStack_78);
  if (iVar1 != 0) {
    iVar2 = *DAT_0051b134;
    *(undefined4 *)(iVar2 + 0x114) = 0;
    *(undefined4 *)(iVar2 + 0x118) = 0;
    FUN_0051565c(iVar1);
    return iVar1;
  }
  return 0;
}

