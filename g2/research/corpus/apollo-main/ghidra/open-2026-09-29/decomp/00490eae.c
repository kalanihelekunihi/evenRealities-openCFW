
undefined8 FUN_00490eae(int param_1,int param_2)

{
  undefined4 uVar1;
  byte bVar2;
  uint *puVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  undefined4 unaff_r7;
  
  if ((*(byte *)(param_2 + 0x16) & 0xf) == 2) {
    if (*(short *)(param_2 + 0x12) == 1) {
      puVar3 = *(uint **)(param_2 + 0x1c);
      uVar4 = (uint)(byte)*puVar3;
      uVar6 = 0;
    }
    else if (*(short *)(param_2 + 0x12) == 2) {
      puVar3 = *(uint **)(param_2 + 0x1c);
      uVar4 = (uint)(ushort)*puVar3;
      uVar6 = 0;
    }
    else if (*(short *)(param_2 + 0x12) == 4) {
      puVar3 = *(uint **)(param_2 + 0x1c);
      uVar4 = *puVar3;
      uVar6 = 0;
    }
    else {
      if (*(short *)(param_2 + 0x12) != 8) {
        uVar1 = DAT_004910d4;
        if (*(int *)(param_1 + 0x10) != 0) {
          uVar1 = *(undefined4 *)(param_1 + 0x10);
        }
        *(undefined4 *)(param_1 + 0x10) = uVar1;
        uVar1 = 0;
        goto LAB_00490f70;
      }
      puVar3 = *(uint **)(param_2 + 0x1c);
      uVar4 = *puVar3;
      uVar6 = puVar3[1];
    }
    uVar1 = FUN_00490ce0(param_1,puVar3,uVar4,uVar6);
  }
  else {
    if (*(short *)(param_2 + 0x12) == 1) {
      iVar5 = (int)**(char **)(param_2 + 0x1c);
      iVar7 = iVar5 >> 0x1f;
    }
    else if (*(short *)(param_2 + 0x12) == 2) {
      iVar5 = (int)**(short **)(param_2 + 0x1c);
      iVar7 = iVar5 >> 0x1f;
    }
    else if (*(short *)(param_2 + 0x12) == 4) {
      iVar5 = **(int **)(param_2 + 0x1c);
      iVar7 = iVar5 >> 0x1f;
    }
    else {
      if (*(short *)(param_2 + 0x12) != 8) {
        uVar1 = DAT_004910d4;
        if (*(int *)(param_1 + 0x10) != 0) {
          uVar1 = *(undefined4 *)(param_1 + 0x10);
        }
        *(undefined4 *)(param_1 + 0x10) = uVar1;
        uVar1 = 0;
        goto LAB_00490f70;
      }
      iVar5 = **(int **)(param_2 + 0x1c);
      iVar7 = (*(int **)(param_2 + 0x1c))[1];
    }
    bVar2 = *(byte *)(param_2 + 0x16) & 0xf;
    if (bVar2 == 3) {
      uVar1 = FUN_00490d08();
    }
    else {
      uVar1 = FUN_00490ce0(param_1,bVar2,iVar5,iVar7);
    }
  }
LAB_00490f70:
  return CONCAT44(unaff_r7,uVar1);
}

