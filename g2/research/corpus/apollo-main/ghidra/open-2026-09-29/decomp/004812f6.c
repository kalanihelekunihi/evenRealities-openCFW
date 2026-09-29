
undefined4 FUN_004812f6(char param_1,char param_2,uint *param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  undefined4 uVar3;
  uint local_34 [7];
  undefined4 uStack_18;
  
  uVar3 = 0;
  for (uVar2 = 0; uVar2 < 7; uVar2 = uVar2 + 1) {
    local_34[uVar2] = 0xffffffff;
  }
  uStack_18 = param_4;
  uVar2 = FUN_00473940();
  if (param_1 == '\0') {
    if (param_2 != '\0') {
      local_34[0] = *DAT_00481768;
      local_34[1] = *DAT_0048176c;
      local_34[2] = *DAT_00481770;
      local_34[3] = *DAT_00481774;
      local_34[4] = *DAT_00481778;
      local_34[5] = *DAT_0048177c;
      local_34[6] = *DAT_00481780;
    }
    *param_3 = *DAT_004817a0 & local_34[0];
    param_3[1] = *DAT_004817a4 & local_34[1];
    param_3[2] = *DAT_004817a8 & local_34[2];
    param_3[3] = *DAT_004817ac & local_34[3];
    param_3[4] = *DAT_004817b0 & local_34[4];
    param_3[5] = *DAT_004817b4 & local_34[5];
    param_3[6] = *DAT_004817b8 & local_34[6];
  }
  else if (param_1 == '\x01') {
    if (param_2 != '\0') {
      local_34[0] = *DAT_00481784;
      local_34[1] = *DAT_00481788;
      local_34[2] = *DAT_0048178c;
      local_34[3] = *DAT_00481790;
      local_34[4] = *DAT_00481794;
      local_34[5] = *DAT_00481798;
      local_34[6] = *DAT_0048179c;
    }
    *param_3 = *DAT_004817bc & local_34[0];
    param_3[1] = *DAT_004817c0 & local_34[1];
    param_3[2] = *DAT_004817c4 & local_34[2];
    param_3[3] = *DAT_004817c8 & local_34[3];
    param_3[4] = *DAT_004817cc & local_34[4];
    param_3[5] = *DAT_004817d0 & local_34[5];
    param_3[6] = *DAT_004817d4 & local_34[6];
  }
  else {
    uVar3 = 6;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return uVar3;
}

