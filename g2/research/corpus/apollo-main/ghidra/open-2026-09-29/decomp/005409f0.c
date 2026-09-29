
void FUN_005409f0(int param_1,int param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  uint in_fpscr;
  undefined4 uVar10;
  int local_90;
  uint local_8c;
  int local_88;
  int local_84;
  int local_80;
  int local_7c;
  int local_78;
  int local_74;
  undefined4 local_70;
  undefined4 local_6c;
  undefined1 auStack_60 [16];
  undefined4 local_50 [2];
  undefined4 local_48;
  undefined4 local_40;
  undefined4 local_3c;
  undefined1 auStack_2c [16];
  
  iVar2 = FUN_00450bcc(auStack_2c,param_2 + 0x1c,param_1 + 0x38);
  if (iVar2 != 0) {
    iVar2 = *(int *)(param_1 + 0x48);
    piVar8 = (int *)(iVar2 + 4);
    iVar7 = *(int *)(param_1 + 0x4c);
    if (-1 < (int)((uint)*(byte *)(param_2 + 0x30) << 0x1f)) {
      FUN_004b0730(iVar7,1);
      FUN_00522a16(0);
      local_90 = *(int *)(param_2 + 0x20) + -1;
      FUN_00450b5c(&local_70,*(undefined4 *)(param_1 + 0x38),*(undefined4 *)(param_1 + 0x3c),
                   *(undefined4 *)(param_1 + 0x40));
      FUN_00450bb2(&local_70,-*piVar8,-*(int *)(iVar2 + 8));
      uVar3 = FUN_004515a4(&local_70);
      uVar4 = FUN_00451598(&local_70);
      FUN_00522ae0(local_70,local_6c,uVar4,uVar3);
      local_90 = *(int *)(param_1 + 0x44);
      FUN_00450b5c(&local_70,*(undefined4 *)(param_1 + 0x38),*(int *)(param_2 + 0x28) + 1,
                   *(undefined4 *)(param_1 + 0x40));
      FUN_00450bb2(&local_70,-*piVar8,-*(int *)(iVar2 + 8));
      uVar3 = FUN_004515a4(&local_70);
      uVar4 = FUN_00451598(&local_70);
      FUN_00522ae0(local_70,local_6c,uVar4,uVar3);
      local_90 = *(int *)(param_2 + 0x28);
      FUN_00450b5c(&local_70,*(undefined4 *)(param_1 + 0x38),*(undefined4 *)(param_2 + 0x20),
                   *(int *)(param_2 + 0x1c) + -1);
      FUN_00450bb2(&local_70,-*piVar8,-*(int *)(iVar2 + 8));
      uVar3 = FUN_004515a4(&local_70);
      uVar4 = FUN_00451598(&local_70);
      FUN_00522ae0(local_70,local_6c,uVar4,uVar3);
      local_90 = *(int *)(param_2 + 0x28);
      FUN_00450b5c(&local_70,*(int *)(param_2 + 0x24) + 1,*(undefined4 *)(param_2 + 0x20),
                   *(undefined4 *)(param_1 + 0x40));
      FUN_00450bb2(&local_70,-*piVar8,-*(int *)(iVar2 + 8));
      uVar3 = FUN_004515a4(&local_70);
      uVar4 = FUN_00451598(&local_70);
      FUN_00522ae0(local_70,local_6c,uVar4,uVar3);
    }
    iVar9 = *(int *)(param_2 + 0x2c);
    iVar5 = FUN_00451598(param_2 + 0x1c);
    iVar6 = FUN_004515a4(param_2 + 0x1c);
    if (iVar5 < iVar6) {
      iVar5 = FUN_00451598(param_2 + 0x1c);
    }
    else {
      iVar5 = FUN_004515a4(param_2 + 0x1c);
    }
    if (iVar5 >> 1 < iVar9) {
      iVar9 = iVar5 >> 1;
    }
    cVar1 = FUN_004b0b5a(iVar7,iVar9,iVar9);
    if (cVar1 == '\x01') {
      local_88 = 1;
      local_8c = *(uint *)(*(int *)(iVar7 + 0x40) + 8) & 0xffff;
      local_90 = 9;
      FUN_004b1298(1,*(undefined4 *)(*(int *)(iVar7 + 0x40) + 0x10),
                   *(uint *)(*(int *)(iVar7 + 0x40) + 4) & 0xffff,
                   *(uint *)(*(int *)(iVar7 + 0x40) + 4) >> 0x10);
      local_8c = 0;
      local_90 = -1;
      FUN_004b06c0(iVar7,1,1,0xffffffff);
      FUN_004b1516(0,0,iVar9,iVar9);
      FUN_00522a16(0);
      FUN_00522ae0(0,0,iVar9,iVar9);
      FUN_00522a16(0xffffffff);
      uVar10 = VectorSignedToFloat(iVar9,(byte)(in_fpscr >> 0x16) & 3);
      uVar4 = VectorSignedFixedToFloat(iVar9,0x20,1);
      uVar3 = VectorSignedToFloat(iVar9,(byte)(in_fpscr >> 0x16) & 3);
      FUN_0052330c(DAT_00540ebc,uVar3,uVar4,uVar10,DAT_00540eb8,DAT_00540eb4);
      FUN_004b1548();
      local_88 = 1;
      local_8c = *(uint *)(*(int *)(iVar7 + 0x40) + 8) & 0xffff;
      local_90 = 8;
      FUN_004b1298(1,*(undefined4 *)(*(int *)(iVar7 + 0x40) + 0x10),
                   *(uint *)(*(int *)(iVar7 + 0x40) + 4) & 0xffff,
                   *(uint *)(*(int *)(iVar7 + 0x40) + 4) >> 0x10);
      local_8c = 0;
      local_90 = -1;
      FUN_004b06c0(iVar7,0x400,0,1);
      FUN_004b146c(0xffffffff);
      iVar5 = *(int *)(iVar2 + 4);
      iVar7 = *(int *)(iVar2 + 8);
      local_78 = *(undefined4 *)(param_2 + 0x24);
      local_80 = (*(int *)(param_2 + 0x24) - iVar9) + 1;
      local_7c = *(int *)(param_2 + 0x20);
      local_74 = iVar9 + *(int *)(param_2 + 0x20) + -1;
      FUN_005409dc(auStack_60,&local_80);
      iVar2 = FUN_00450bcc(&local_90,auStack_60,param_1 + 0x38);
      if (iVar2 != 0) {
        FUN_00561810(local_50);
        uVar4 = VectorSignedToFloat(iVar7 - local_7c,(byte)(in_fpscr >> 0x16) & 3);
        uVar3 = VectorSignedToFloat(iVar5 - local_80,(byte)(in_fpscr >> 0x16) & 3);
        FUN_00561856(uVar3,uVar4,local_50);
        FUN_005226e8(local_50);
        FUN_00522ae0(local_90 - iVar5,local_8c - iVar7,(local_88 - local_90) + 1,
                     (local_84 - local_8c) + 1);
      }
      local_78 = *(undefined4 *)(param_2 + 0x24);
      local_80 = (*(int *)(param_2 + 0x24) - iVar9) + 1;
      local_7c = (*(int *)(param_2 + 0x28) - iVar9) + 1;
      local_74 = *(undefined4 *)(param_2 + 0x28);
      FUN_005409dc(auStack_60,&local_80);
      iVar2 = FUN_00450bcc(&local_90,auStack_60,param_1 + 0x38);
      if (iVar2 != 0) {
        FUN_00561810(local_50);
        local_40 = DAT_00540ecc;
        local_48 = VectorSignedToFloat(local_80 - iVar5,(byte)(in_fpscr >> 0x16) & 3);
        local_3c = VectorSignedToFloat((local_7c + iVar9 + -1) - iVar7,(byte)(in_fpscr >> 0x16) & 3)
        ;
        FUN_00561b38(local_50);
        FUN_005226e8(local_50);
        FUN_00522ae0(local_90 - iVar5,local_8c - iVar7,(local_88 - local_90) + 1,
                     (local_84 - local_8c) + 1);
      }
      local_80 = *(int *)(param_2 + 0x1c);
      local_78 = iVar9 + *(int *)(param_2 + 0x1c) + -1;
      local_7c = (*(int *)(param_2 + 0x28) - iVar9) + 1;
      local_74 = *(undefined4 *)(param_2 + 0x28);
      FUN_005409dc(auStack_60,&local_80);
      iVar2 = FUN_00450bcc(&local_90,auStack_60,param_1 + 0x38);
      if (iVar2 != 0) {
        FUN_00561810(local_50);
        local_50[0] = 0xbf800000;
        local_40 = 0xbf800000;
        local_48 = VectorSignedToFloat((local_80 + iVar9 + -1) - iVar5,(byte)(in_fpscr >> 0x16) & 3)
        ;
        local_3c = VectorSignedToFloat((local_7c + iVar9 + -1) - iVar7,(byte)(in_fpscr >> 0x16) & 3)
        ;
        FUN_00561b38(local_50);
        FUN_005226e8(local_50);
        FUN_00522ae0(local_90 - iVar5,local_8c - iVar7,(local_88 - local_90) + 1,
                     (local_84 - local_8c) + 1);
      }
      local_80 = *(int *)(param_2 + 0x1c);
      local_78 = iVar9 + *(int *)(param_2 + 0x1c) + -1;
      local_7c = *(int *)(param_2 + 0x20);
      local_74 = iVar9 + *(int *)(param_2 + 0x20) + -1;
      FUN_005409dc(auStack_60,&local_80);
      iVar2 = FUN_00450bcc(&local_90,auStack_60,param_1 + 0x38);
      if (iVar2 != 0) {
        FUN_00561810(local_50);
        local_50[0] = DAT_00540ecc;
        local_48 = VectorSignedToFloat((local_80 + iVar9 + -1) - iVar5,(byte)(in_fpscr >> 0x16) & 3)
        ;
        local_3c = VectorSignedToFloat(local_7c - iVar7,(byte)(in_fpscr >> 0x16) & 3);
        FUN_00561b38(local_50);
        FUN_005226e8(local_50);
        FUN_00522ae0(local_90 - iVar5,local_8c - iVar7,(local_88 - local_90) + 1,
                     (local_84 - local_8c) + 1);
      }
      uVar3 = FUN_005144fa();
      FUN_00514cf2(uVar3);
      FUN_00514d00(uVar3);
      FUN_00514384(uVar3);
    }
    else {
      local_90 = DAT_00540ec0;
      FUN_0044d25c(3,DAT_00540ec8,0x66,DAT_00540ec4);
    }
  }
  return;
}

