
longlong FUN_004c8d8c(int param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  byte *pbVar4;
  
  pbVar4 = param_2;
  iVar1 = FUN_004c81a2(param_1);
  if (iVar1 != 0) {
    uVar2 = *(uint *)(param_2 + 8);
    uVar3 = *(undefined4 *)(param_2 + 4);
    iVar1 = FUN_0048b010(DAT_004c8ee0,*(uint *)(param_1 + 0x24) & 0xffff,
                         *(uint *)(param_1 + 0x24) >> 0x10,*(uint *)(param_1 + 0x20) >> 8 & 0xff,
                         *(uint *)(param_1 + 0x28) & 0xffff,param_3,param_4);
    if (iVar1 == 0) {
      pbVar4 = DAT_004c8ee4;
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x45d,DAT_004c8ee8,DAT_004c8ee4
                   ,uVar3,uVar2);
    }
    else if (*(uint *)(iVar1 + 0xc) < uVar2) {
      pbVar4 = DAT_004c8eec;
      FUN_0044d25c(3,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x462,DAT_004c8ee8,DAT_004c8eec
                   ,uVar2,*(undefined4 *)(iVar1 + 0xc));
      FUN_0048b216(iVar1);
    }
    else if ((*param_2 & 0xf) == 1) {
      pbVar4 = DAT_004c8ef0;
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x47b,DAT_004c8ee8);
      FUN_0048b216(iVar1);
    }
    else if ((*param_2 & 0xf) == 2) {
      pbVar4 = DAT_004c8ef4;
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x48c,DAT_004c8ee8);
      FUN_0048b216(iVar1);
    }
    else {
      pbVar4 = DAT_004c8ef8;
      FUN_0044d25c(2,PTR_s_D__01_workspace_s200_ap510b_iar__004c8ea0,0x493,DAT_004c8ee8,DAT_004c8ef8
                   ,*param_2 & 0xf);
      FUN_0048b216(iVar1);
    }
  }
  return ZEXT48(pbVar4) << 0x20;
}

