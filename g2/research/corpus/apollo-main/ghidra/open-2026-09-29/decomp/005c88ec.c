
void FUN_005c88ec(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  int iVar10;
  int local_50;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c;
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  local_50 = FUN_005c78f6(param_1,0);
  iVar2 = FUN_005c7900(param_1,0);
  local_4c = FUN_005c816c(param_1);
  iVar3 = FUN_004997f8(*(undefined4 *)(param_1 + 0x2c));
  iVar4 = (*(code *)*DAT_005c8fd4)(iVar3,local_4c);
  iVar5 = (*(code *)*DAT_005c8fc8)(iVar3 + iVar4,0);
  iVar6 = *(int *)(local_50 + 0xc);
  iVar7 = FUN_005c8fe8(iVar5);
  iVar10 = iVar5;
  if (iVar7 != 0) {
    iVar10 = 0x20;
  }
  iVar10 = FUN_004d57f4(local_50,iVar10,0);
  FUN_00499830(*(undefined4 *)(param_1 + 0x2c),local_4c,&local_40);
  uVar8 = FUN_004997f8(*(undefined4 *)(param_1 + 0x2c));
  cVar1 = FUN_0044c448(*(undefined4 *)(param_1 + 0x2c),0,uVar8);
  if (((*(int *)(*(int *)(param_1 + 0x2c) + 0x1c) <
        iVar10 + *(int *)(*(int *)(param_1 + 0x2c) + 0x14) + local_40) &&
      ((*(byte *)(param_1 + 0x70) & 0xf) >> 3 == 0)) && (cVar1 != '\x03')) {
    local_40 = 0;
    local_3c = iVar2 + iVar6 + local_3c;
    uVar8 = 0;
    if (iVar5 != 0) {
      uVar9 = (*(code *)*DAT_005c8fd8)(iVar3 + iVar4);
      iVar4 = iVar4 + (uVar9 & 0xff);
      uVar8 = (*(code *)*DAT_005c8fc8)(iVar3 + iVar4,0);
    }
    iVar10 = FUN_005c8fe8(uVar8);
    if (iVar10 != 0) {
      uVar8 = 0x20;
    }
    iVar10 = FUN_004d57f4(local_50,uVar8,0);
  }
  *(int *)(param_1 + 0x60) = iVar4;
  iVar2 = FUN_005c78de(param_1,0x60000);
  iVar3 = FUN_005c78b6(param_1,0x60000);
  iVar4 = FUN_005c78c0(param_1,0x60000);
  iVar5 = FUN_005c78ca(param_1,0x60000);
  iVar7 = FUN_005c78d4(param_1,0x60000);
  local_38 = local_40 - (iVar2 + iVar5);
  local_34 = local_3c - (iVar2 + iVar3);
  local_30 = iVar10 + iVar2 + iVar7 + local_40 + -1;
  local_2c = iVar6 + iVar2 + iVar4 + local_3c + -1;
  FUN_005c78a4(&local_50,param_1 + 0x50);
  local_50 = *(int *)(*(int *)(param_1 + 0x2c) + 0x14) + local_50;
  local_4c = *(int *)(*(int *)(param_1 + 0x2c) + 0x18) + local_4c;
  local_48 = *(int *)(*(int *)(param_1 + 0x2c) + 0x14) + local_48;
  local_44 = *(int *)(*(int *)(param_1 + 0x2c) + 0x18) + local_44;
  FUN_004405d4(param_1,&local_50);
  FUN_005c78a4(param_1 + 0x50,&local_38);
  FUN_005c78a4(&local_50,param_1 + 0x50);
  local_50 = *(int *)(*(int *)(param_1 + 0x2c) + 0x14) + local_50;
  local_4c = *(int *)(*(int *)(param_1 + 0x2c) + 0x18) + local_4c;
  local_48 = *(int *)(*(int *)(param_1 + 0x2c) + 0x14) + local_48;
  local_44 = *(int *)(*(int *)(param_1 + 0x2c) + 0x18) + local_44;
  FUN_004405d4(param_1,&local_50);
  return;
}

