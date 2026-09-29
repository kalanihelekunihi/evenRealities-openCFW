
undefined4 FUN_004901d6(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint *puVar6;
  int *piVar7;
  int local_28;
  int iStack_24;
  uint local_20;
  uint uStack_1c;
  int local_18;
  int iStack_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  if ((*(byte *)(param_2 + 0x16) & 0xf) == 2) {
    iVar1 = FUN_0048f5b8(param_1,&local_20);
    if (iVar1 == 0) {
      uVar2 = 0;
    }
    else {
      if (*(short *)(param_2 + 0x12) == 8) {
        puVar6 = *(uint **)(param_2 + 0x1c);
        *puVar6 = local_20;
        puVar6[1] = uStack_1c;
        uVar3 = local_20;
        uVar4 = uStack_1c;
      }
      else if (*(short *)(param_2 + 0x12) == 4) {
        **(uint **)(param_2 + 0x1c) = local_20;
        uVar3 = **(uint **)(param_2 + 0x1c);
        uVar4 = 0;
      }
      else if (*(short *)(param_2 + 0x12) == 2) {
        **(undefined2 **)(param_2 + 0x1c) = (short)local_20;
        uVar3 = (uint)**(ushort **)(param_2 + 0x1c);
        uVar4 = 0;
      }
      else {
        if (*(short *)(param_2 + 0x12) != 1) {
          uVar2 = DAT_004905c4;
          if (*(int *)(param_1 + 0xc) != 0) {
            uVar2 = *(undefined4 *)(param_1 + 0xc);
          }
          *(undefined4 *)(param_1 + 0xc) = uVar2;
          return 0;
        }
        **(undefined1 **)(param_2 + 0x1c) = (char)local_20;
        uVar3 = (uint)**(byte **)(param_2 + 0x1c);
        uVar4 = 0;
      }
      if ((uVar4 == uStack_1c) && (uVar3 == local_20)) {
        uVar2 = 1;
      }
      else {
        uVar2 = DAT_004905c8;
        if (*(int *)(param_1 + 0xc) != 0) {
          uVar2 = *(undefined4 *)(param_1 + 0xc);
        }
        *(undefined4 *)(param_1 + 0xc) = uVar2;
        uVar2 = 0;
      }
    }
  }
  else {
    if ((*(byte *)(param_2 + 0x16) & 0xf) == 3) {
      iVar1 = FUN_00490150(param_1,&local_28);
      if (iVar1 == 0) {
        return 0;
      }
    }
    else {
      iVar1 = FUN_0048f5b8(param_1,&local_18);
      if (iVar1 == 0) {
        return 0;
      }
      if (*(short *)(param_2 + 0x12) == 8) {
        local_28 = local_18;
        iStack_24 = iStack_14;
      }
      else {
        iStack_24 = local_18 >> 0x1f;
        local_28 = local_18;
      }
    }
    if (*(short *)(param_2 + 0x12) == 8) {
      piVar7 = *(int **)(param_2 + 0x1c);
      *piVar7 = local_28;
      piVar7[1] = iStack_24;
      iVar1 = local_28;
      iVar5 = iStack_24;
    }
    else if (*(short *)(param_2 + 0x12) == 4) {
      **(int **)(param_2 + 0x1c) = local_28;
      iVar1 = **(int **)(param_2 + 0x1c);
      iVar5 = iVar1 >> 0x1f;
    }
    else if (*(short *)(param_2 + 0x12) == 2) {
      **(undefined2 **)(param_2 + 0x1c) = (short)local_28;
      iVar1 = (int)**(short **)(param_2 + 0x1c);
      iVar5 = iVar1 >> 0x1f;
    }
    else {
      if (*(short *)(param_2 + 0x12) != 1) {
        uVar2 = DAT_004905c4;
        if (*(int *)(param_1 + 0xc) != 0) {
          uVar2 = *(undefined4 *)(param_1 + 0xc);
        }
        *(undefined4 *)(param_1 + 0xc) = uVar2;
        return 0;
      }
      **(undefined1 **)(param_2 + 0x1c) = (char)local_28;
      iVar1 = (int)**(char **)(param_2 + 0x1c);
      iVar5 = iVar1 >> 0x1f;
    }
    if ((iVar5 == iStack_24) && (iVar1 == local_28)) {
      uVar2 = 1;
    }
    else {
      uVar2 = DAT_004905c8;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar2 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar2;
      uVar2 = 0;
    }
  }
  return uVar2;
}

