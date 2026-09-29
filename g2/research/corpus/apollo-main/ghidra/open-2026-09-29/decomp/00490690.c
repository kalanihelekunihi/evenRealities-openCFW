
undefined4 FUN_00490690(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  ushort uVar7;
  undefined8 uVar8;
  undefined1 auStack_30 [12];
  int local_24;
  int local_20;
  undefined4 uStack_1c;
  
  uVar1 = **(ushort **)(param_2 + 0x20);
  if (uVar1 == 0) {
    uVar3 = 1;
  }
  else if (((*(byte *)(param_2 + 0x16) & 0xc0) == 0x80) || (uVar1 <= *(ushort *)(param_2 + 0x14))) {
    uStack_1c = param_4;
    if ((*(byte *)(param_2 + 0x16) & 0xf) < 6) {
      uVar8 = FUN_00490d4a(param_1,2,*(undefined2 *)(param_2 + 0x10));
      uVar6 = (uint)((ulonglong)uVar8 >> 0x20);
      if ((int)uVar8 == 0) {
        return 0;
      }
      if ((*(byte *)(param_2 + 0x16) & 0xf) == 4) {
        iVar5 = (uint)uVar1 << 2;
      }
      else if ((*(byte *)(param_2 + 0x16) & 0xf) == 5) {
        iVar5 = (uint)uVar1 << 3;
      }
      else {
        FUN_0048949c(auStack_30,0x14);
        uVar3 = *(undefined4 *)(param_2 + 0x1c);
        for (uVar7 = 0; uVar6 = (uint)uVar1, uVar7 < uVar6; uVar7 = uVar7 + 1) {
          iVar5 = FUN_00490eae(auStack_30,param_2);
          if (iVar5 == 0) {
            if (param_1[4] == 0) {
              iVar5 = DAT_004910b8;
              if (local_20 != 0) {
                iVar5 = local_20;
              }
            }
            else {
              iVar5 = param_1[4];
            }
            param_1[4] = iVar5;
            return 0;
          }
          *(uint *)(param_2 + 0x1c) = *(int *)(param_2 + 0x1c) + (uint)*(ushort *)(param_2 + 0x12);
        }
        *(undefined4 *)(param_2 + 0x1c) = uVar3;
        iVar5 = local_24;
      }
      iVar4 = FUN_00490ce0(param_1,uVar6,iVar5,0);
      if (iVar4 == 0) {
        return 0;
      }
      if (*param_1 == 0) {
        uVar3 = FUN_00490616(param_1,0,iVar5);
        return uVar3;
      }
      for (uVar7 = 0; uVar7 < uVar1; uVar7 = uVar7 + 1) {
        if (((*(byte *)(param_2 + 0x16) & 0xf) == 4) || ((*(byte *)(param_2 + 0x16) & 0xf) == 5)) {
          iVar5 = FUN_00490f72(param_1,param_2);
          if (iVar5 == 0) {
            return 0;
          }
        }
        else {
          iVar5 = FUN_00490eae(param_1,param_2);
          if (iVar5 == 0) {
            return 0;
          }
        }
        *(uint *)(param_2 + 0x1c) = *(int *)(param_2 + 0x1c) + (uint)*(ushort *)(param_2 + 0x12);
      }
    }
    else {
      for (uVar7 = 0; uVar7 < uVar1; uVar7 = uVar7 + 1) {
        if (((*(byte *)(param_2 + 0x16) & 0xc0) == 0x80) &&
           (((*(byte *)(param_2 + 0x16) & 0xf) == 7 || ((*(byte *)(param_2 + 0x16) & 0xf) == 6)))) {
          uVar3 = *(undefined4 *)(param_2 + 0x1c);
          *(undefined4 *)(param_2 + 0x1c) = **(undefined4 **)(param_2 + 0x1c);
          if (*(int *)(param_2 + 0x1c) == 0) {
            uVar8 = FUN_00490d66(param_1,param_2);
            if (((int)uVar8 == 0) ||
               (iVar5 = FUN_00490ce0(param_1,(int)((ulonglong)uVar8 >> 0x20),0,0), iVar5 == 0)) {
              cVar2 = '\0';
            }
            else {
              cVar2 = '\x01';
            }
          }
          else {
            cVar2 = FUN_00490a46(param_1,param_2);
          }
          *(undefined4 *)(param_2 + 0x1c) = uVar3;
          if (cVar2 == '\0') {
            return 0;
          }
        }
        else {
          iVar5 = FUN_00490a46(param_1,param_2);
          if (iVar5 == 0) {
            return 0;
          }
        }
        *(uint *)(param_2 + 0x1c) = *(int *)(param_2 + 0x1c) + (uint)*(ushort *)(param_2 + 0x12);
      }
    }
    uVar3 = 1;
  }
  else {
    iVar5 = DAT_004910b4;
    if (param_1[4] != 0) {
      iVar5 = param_1[4];
    }
    param_1[4] = iVar5;
    uVar3 = 0;
  }
  return uVar3;
}

