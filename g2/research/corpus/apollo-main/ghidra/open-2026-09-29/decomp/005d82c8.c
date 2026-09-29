
int FUN_005d82c8(undefined4 param_1,short *param_2,int param_3,uint param_4)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  undefined1 auStack_a8 [24];
  int local_90;
  undefined1 auStack_8c [92];
  undefined1 local_30;
  undefined1 local_2f;
  undefined1 local_2e;
  undefined1 local_2d;
  undefined1 local_2c;
  uint uStack_28;
  
  if ((param_2[1] == 0) || (*param_2 == 0)) {
    iVar2 = 0;
  }
  else {
    uStack_28 = param_4;
    iVar2 = FUN_005d784a(auStack_a8,param_2,param_1,param_3);
    if (iVar2 == 0) {
      iVar6 = *(int *)(local_90 + 200);
      uVar8 = *(undefined4 *)(local_90 + 0x194);
      bVar1 = false;
      uVar3 = FT_MulFix(*(undefined4 *)(param_3 + 0x1a0),uVar8);
      uVar5 = uVar3 + 0x20 & 0xffffffc0;
      if ((uVar5 != 0) && (uVar3 != uVar5)) {
        bVar1 = true;
        uVar4 = FT_MulDiv(uVar8,uVar5,uVar3);
        iVar7 = iVar6;
        if ((int)uVar5 < (int)uVar3) {
          iVar7 = iVar6 - iVar6 / 0x32;
        }
        FUN_005d8a48(local_90,iVar7,uVar4,0,0);
      }
      local_30 = 1;
      local_2f = 1;
      if (((param_4 & 0xff) == 2) || ((param_4 & 0xff) == 3)) {
        local_2e = 1;
      }
      else {
        local_2e = 0;
      }
      if (((param_4 & 0xff) == 2) || ((param_4 & 0xff) == 4)) {
        local_2d = 1;
      }
      else {
        local_2d = 0;
      }
      local_2c = (param_4 & 0xff) != 1;
      for (iVar7 = 0; iVar7 < 2; iVar7 = iVar7 + 1) {
        FUN_005d77ca(auStack_a8,iVar7);
        FUN_005d7a6c(auStack_a8);
        FUN_005d75ee(auStack_8c + iVar7 * 0x28,local_90,iVar7,auStack_a8);
        FUN_005d7d1c(auStack_a8,iVar7);
        if (iVar7 == 1) {
          FUN_005d7e1a(param_3 + 0x19c,auStack_a8);
        }
        FUN_005d7f04(auStack_a8,iVar7);
        FUN_005d7f90(auStack_a8,iVar7);
        FUN_005d816c(auStack_a8,iVar7);
        FUN_005d7802(auStack_a8,iVar7);
        if (bVar1) {
          FUN_005d8a48(local_90,iVar6,uVar8,0,0);
        }
      }
    }
    FUN_005d7742(auStack_a8);
  }
  return iVar2;
}

