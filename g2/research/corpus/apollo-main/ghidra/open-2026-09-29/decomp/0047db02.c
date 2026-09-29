
undefined8 FUN_0047db02(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  
  iVar3 = FUN_0047da16();
  iVar1 = DAT_0047dc30;
  if (iVar3 == 0) {
    uVar4 = 0;
  }
  else {
    if (10 < *(uint *)(DAT_0047dc30 + 8)) {
      FUN_004733ee(DAT_0047dc40,*(undefined4 *)(DAT_0047dc30 + 8));
    }
    uVar4 = DAT_0047dc44;
    FUN_0044b728(DAT_0047dc44,0x80,DAT_0047dc48,param_1,param_2,param_3,param_4);
    iVar3 = file_open(uVar4,&DAT_0047dc24);
    if (iVar3 != 0) {
      file_seek(iVar3,0,2);
      iVar5 = file_tell(iVar3);
      file_close(iVar3);
      if (DAT_0047dc4c <= iVar5) {
        file_remove(uVar4);
        FUN_004733ee(DAT_0047dc50);
      }
    }
    iVar3 = file_open(uVar4,&DAT_0047dc28);
    uVar2 = DAT_0047dc5c;
    if (iVar3 == 0) {
      FUN_004733ee(DAT_0047dc54,uVar4);
    }
    else {
      param_2 = DAT_0047dc58;
      if (*(int *)(iVar1 + 0x10) == 0) {
        param_2 = &DAT_0047dc2c;
      }
      uVar6 = *(undefined4 *)(iVar1 + 0x14);
      uVar7 = *(undefined4 *)(iVar1 + 0xc);
      iVar5 = FUN_0044b728(DAT_0047dc5c,0x200,DAT_0047dc60,*(undefined4 *)(iVar1 + 8),param_2,uVar7,
                           uVar6);
      if (0 < iVar5) {
        file_write(uVar2,1,iVar5,iVar3);
      }
      iVar5 = file_write(iVar1 + 0x18,1,*(undefined4 *)(iVar1 + 0xc),iVar3);
      if (iVar5 != *(int *)(iVar1 + 0xc)) {
        FUN_004733ee(DAT_0047dc64,iVar5,*(undefined4 *)(iVar1 + 0xc));
      }
      uVar2 = DAT_0047dc68;
      iVar5 = FUN_0044b728(DAT_0047dc68,0x100,DAT_0047dc6c,*(undefined4 *)(iVar1 + 8),param_2,uVar7,
                           uVar6);
      if (0 < iVar5) {
        file_write(uVar2,1,iVar5,iVar3);
      }
      file_flush(iVar3);
      file_close(iVar3);
      FUN_004733ee(DAT_0047dc70,*(undefined4 *)(iVar1 + 8),uVar4);
    }
    uVar4 = *(undefined4 *)(iVar1 + 8);
    FUN_0043c0e4(iVar1,0x11ac,0);
    *(undefined4 *)(iVar1 + 8) = uVar4;
    uVar4 = 1;
  }
  return CONCAT44(param_2,uVar4);
}

