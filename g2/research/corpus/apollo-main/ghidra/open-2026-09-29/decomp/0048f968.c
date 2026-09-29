
uint FUN_0048f968(int param_1,char param_2,int param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  byte bVar5;
  ushort *puVar6;
  undefined1 auStack_50 [8];
  int local_48;
  undefined1 auStack_40 [40];
  undefined4 uStack_18;
  
  bVar5 = *(byte *)(param_3 + 0x16) & 0x30;
  uStack_18 = param_4;
  if ((*(byte *)(param_3 + 0x16) & 0x30) == 0) {
    uVar4 = FUN_0048f7f4(param_1,param_2,param_3);
  }
  else if (bVar5 == 0x10) {
    if (*(int *)(param_3 + 0x20) != 0) {
      **(undefined1 **)(param_3 + 0x20) = 1;
    }
    uVar4 = FUN_0048f7f4(param_1,param_2,param_3);
  }
  else if (bVar5 == 0x20) {
    if ((param_2 == '\x02') && ((*(byte *)(param_3 + 0x16) & 0xf) < 6)) {
      bVar5 = 1;
      puVar6 = *(ushort **)(param_3 + 0x20);
      *(uint *)(param_3 + 0x1c) =
           *(int *)(param_3 + 0x18) + (uint)*puVar6 * (uint)*(ushort *)(param_3 + 0x12);
      iVar2 = FUN_0048f77e(param_1,auStack_50);
      if (iVar2 == 0) {
        uVar4 = 0;
      }
      else {
        while( true ) {
          if ((local_48 == 0) || (*(ushort *)(param_3 + 0x14) <= *puVar6)) goto LAB_0048fa12;
          iVar2 = FUN_0048f7f4(auStack_50,0xff,param_3);
          if (iVar2 == 0) break;
          *puVar6 = *puVar6 + 1;
          *(uint *)(param_3 + 0x1c) = *(int *)(param_3 + 0x1c) + (uint)*(ushort *)(param_3 + 0x12);
        }
        bVar5 = 0;
LAB_0048fa12:
        if (local_48 == 0) {
          iVar2 = FUN_0048f7ca(param_1,auStack_50);
          if (iVar2 == 0) {
            uVar4 = 0;
          }
          else {
            uVar4 = (uint)bVar5;
          }
        }
        else {
          uVar3 = DAT_00490538;
          if (*(int *)(param_1 + 0xc) != 0) {
            uVar3 = *(undefined4 *)(param_1 + 0xc);
          }
          *(undefined4 *)(param_1 + 0xc) = uVar3;
          uVar4 = 0;
        }
      }
    }
    else {
      puVar6 = *(ushort **)(param_3 + 0x20);
      *(uint *)(param_3 + 0x1c) =
           *(int *)(param_3 + 0x18) + (uint)*puVar6 * (uint)*(ushort *)(param_3 + 0x12);
      uVar1 = *puVar6;
      *puVar6 = uVar1 + 1;
      if (uVar1 < *(ushort *)(param_3 + 0x14)) {
        uVar4 = FUN_0048f7f4(param_1,param_2,param_3);
      }
      else {
        uVar3 = DAT_00490538;
        if (*(int *)(param_1 + 0xc) != 0) {
          uVar3 = *(undefined4 *)(param_1 + 0xc);
        }
        *(undefined4 *)(param_1 + 0xc) = uVar3;
        uVar4 = 0;
      }
    }
  }
  else if (bVar5 == 0x30) {
    if (((((*(byte *)(param_3 + 0x16) & 0xf) == 8) || ((*(byte *)(param_3 + 0x16) & 0xf) == 9)) &&
        (**(short **)(param_3 + 0x20) != *(short *)(param_3 + 0x10))) &&
       ((((FUN_0043c0e4(*(undefined4 *)(param_3 + 0x1c),*(undefined2 *)(param_3 + 0x12),0),
          *(int *)(*(int *)(param_3 + 0x24) + 8) != 0 ||
          (*(int *)(*(int *)(param_3 + 0x24) + 0xc) != 0)) ||
         (**(int **)(*(int *)(param_3 + 0x24) + 4) != 0)) &&
        ((iVar2 = FUN_004d9384(auStack_40,*(undefined4 *)(param_3 + 0x24),
                               *(undefined4 *)(param_3 + 0x1c)), iVar2 != 0 &&
         (iVar2 = FUN_0048fdf2(auStack_40), iVar2 == 0)))))) {
      uVar3 = DAT_004905a8;
      if (*(int *)(param_1 + 0xc) != 0) {
        uVar3 = *(undefined4 *)(param_1 + 0xc);
      }
      *(undefined4 *)(param_1 + 0xc) = uVar3;
      uVar4 = 0;
    }
    else {
      **(undefined2 **)(param_3 + 0x20) = *(undefined2 *)(param_3 + 0x10);
      uVar4 = FUN_0048f7f4(param_1,param_2,param_3);
    }
  }
  else {
    uVar3 = DAT_00490488;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar3 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar3;
    uVar4 = 0;
  }
  return uVar4;
}

