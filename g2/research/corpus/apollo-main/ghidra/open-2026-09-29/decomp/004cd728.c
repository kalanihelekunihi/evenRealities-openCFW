
int FUN_004cd728(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                int param_5,undefined4 param_6,undefined4 *param_7,undefined4 *param_8)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  int local_30;
  undefined4 local_2c;
  undefined4 local_28;
  
  puVar2 = param_8;
  puVar1 = param_7;
  if (param_5 == 0) {
    *param_7 = 0xffffffff;
    *param_8 = 0;
  }
  else {
    local_30 = param_5 + -1;
    local_28 = param_4;
    uVar3 = FUN_004cd6e4(param_1,&local_30);
    uVar4 = FUN_004cd6e4(param_1,&param_6);
    local_2c = param_2;
    for (; uVar4 < uVar3; uVar3 = uVar3 - (1 << (uVar7 & 0xff))) {
      uVar5 = lfs_ctz(uVar3);
      iVar6 = lfs_npw2((uVar3 - uVar4) + 1);
      uVar7 = lfs_min(iVar6 + -1,uVar5);
      iVar6 = FUN_004ca83c(param_1,local_2c,param_3,4,local_28,uVar7 << 2,&local_28,4);
      local_28 = lfs_fromle32(local_28);
      if (iVar6 != 0) {
        return iVar6;
      }
    }
    *puVar1 = local_28;
    *puVar2 = param_6;
  }
  return 0;
}

