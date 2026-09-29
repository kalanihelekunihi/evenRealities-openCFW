
void FUN_004125a8(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,ushort param_6,uint param_7)

{
  undefined4 uVar1;
  int iVar2;
  undefined2 uVar3;
  uint uVar5;
  uint local_34;
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  uint uVar4;
  
  uStack_28 = param_4;
  do {
    uVar4 = param_7;
    uVar3 = (undefined2)uVar4;
    for (param_7 = (uint)param_6; 1 < (uVar4 & 0xffff) - param_7;
        param_7 = param_7 + ((uVar4 & 0xffff) - param_7 >> 1)) {
      local_34 = 0;
      iVar2 = FUN_004112b4(param_1,param_5,0,0xffffffff,param_3,param_4,DAT_00412f84,0,
                           param_7 & 0xffff,uVar4 & 0xffff,(int)(short)-(short)param_7,DAT_00413214,
                           &local_34);
      if (iVar2 != 0) {
        return;
      }
      if (*(int *)(*(int *)(param_1 + 0x68) + 0x4c) == 0) {
        uVar5 = *(uint *)(*(int *)(param_1 + 0x68) + 0x1c);
      }
      else {
        uVar5 = *(uint *)(*(int *)(param_1 + 0x68) + 0x4c);
      }
      if ((uVar4 & 0xffff) - param_7 < 0xff) {
        uVar1 = lfs_alignup(uVar5 >> 1,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x18));
        uVar5 = lfs_min(uVar5 - 0x28,uVar1);
        if (local_34 <= uVar5) break;
      }
    }
    if (param_7 == param_6) goto LAB_004126b4;
    iVar2 = FUN_00412208(param_1,param_2,param_3,param_4,param_5,param_7 & 0xffff,uVar4 & 0xffff);
    if ((iVar2 != 0) && (iVar2 != -0x1c)) {
      return;
    }
  } while (iVar2 == 0);
  FUN_00415fae(DAT_00413218,DAT_00412f70,0x890,*param_2,param_2[1],&DAT_0041277c);
LAB_004126b4:
  iVar2 = FUN_004122a6(param_1,param_2);
  if (iVar2 != 0) {
    local_30 = *DAT_0041321c;
    uStack_2c = DAT_0041321c[1];
    iVar2 = FUN_00410af2(param_2,&local_30);
    if (iVar2 == 0) {
      iVar2 = FUN_004150e2(param_1);
      uVar1 = DAT_00412f70;
      if (iVar2 < 0) {
        return;
      }
      if (*(uint *)(param_1 + 0x6c) >> 3 < (uint)(*(int *)(param_1 + 0x6c) - iVar2)) {
        FUN_00415fae(DAT_00413220,DAT_00412f70,0x8a5,param_2[2],&DAT_0041277c);
        iVar2 = FUN_00412208(param_1,param_2,param_3,param_4,param_5,param_6,uVar4 & 0xffff);
        if ((iVar2 != 0) && (iVar2 != -0x1c)) {
          return;
        }
        if (iVar2 == 0) {
          uVar3 = 1;
        }
        else {
          FUN_00415fae(DAT_00413224,uVar1,0x8af,&DAT_0041277c);
        }
      }
    }
  }
  FUN_004122d2(param_1,param_2,param_3,param_4,param_5,param_6,uVar3);
  return;
}

