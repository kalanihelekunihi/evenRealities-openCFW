
undefined8 af_property_set(int param_1,undefined4 param_2,uint *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint *local_20;
  undefined4 uStack_1c;
  
  local_20 = param_3;
  uStack_1c = param_4;
  iVar1 = FUN_0046cacc(param_2,DAT_005abc3c);
  iVar3 = DAT_005abc40;
  if (iVar1 == 0) {
    for (iVar1 = 0; *(int *)(DAT_005abc40 + iVar1 * 4) != 0; iVar1 = iVar1 + 1) {
      iVar2 = *(int *)(DAT_005abc40 + iVar1 * 4);
      if (((uint)*(byte *)(iVar2 + 2) == *param_3) && (*(char *)(iVar2 + 4) == '\n')) {
        *(int *)(param_1 + 0xc) = iVar1;
        break;
      }
    }
    if (*(int *)(iVar3 + iVar1 * 4) == 0) {
      iVar3 = 6;
    }
    else {
      iVar3 = 0;
    }
  }
  else {
    iVar3 = FUN_0046cacc(param_2,DAT_005abc44);
    if (iVar3 == 0) {
      *(uint *)(param_1 + 0x10) = *param_3;
      iVar3 = 0;
    }
    else {
      iVar3 = FUN_0046cacc(param_2,DAT_005abc48);
      if (iVar3 == 0) {
        iVar3 = af_property_get_face_globals(*param_3,&local_20,param_1);
        if (iVar3 == 0) {
          local_20[3] = param_3[1];
        }
      }
      else {
        iVar3 = FUN_0046cacc(param_2,DAT_005abc4c);
        if (iVar3 == 0) {
          *(char *)(param_1 + 0x14) = (char)*param_3;
          iVar3 = 0;
        }
        else {
          iVar3 = FUN_0046cacc(param_2,DAT_005abc50);
          if (iVar3 == 0) {
            uVar4 = *param_3;
            uVar5 = param_3[1];
            uVar6 = param_3[2];
            uVar7 = param_3[3];
            uVar9 = param_3[4];
            uVar10 = param_3[5];
            uVar11 = param_3[6];
            uVar8 = param_3[7];
            if ((((((((int)uVar4 < 0) || ((int)uVar6 < 0)) || ((int)uVar9 < 0)) ||
                  (((int)uVar11 < 0 || ((int)uVar5 < 0)))) ||
                 (((int)uVar7 < 0 || (((int)uVar10 < 0 || ((int)uVar8 < 0)))))) ||
                ((int)uVar6 < (int)uVar4)) ||
               (((((int)uVar9 < (int)uVar6 || ((int)uVar11 < (int)uVar9)) || (500 < (int)uVar5)) ||
                (((500 < (int)uVar7 || (500 < (int)uVar10)) || (500 < (int)uVar8)))))) {
              iVar3 = 6;
            }
            else {
              *(uint *)(param_1 + 0x18) = uVar4;
              *(uint *)(param_1 + 0x1c) = uVar5;
              *(uint *)(param_1 + 0x20) = uVar6;
              *(uint *)(param_1 + 0x24) = uVar7;
              *(uint *)(param_1 + 0x28) = uVar9;
              *(uint *)(param_1 + 0x2c) = uVar10;
              *(uint *)(param_1 + 0x30) = uVar11;
              *(uint *)(param_1 + 0x34) = uVar8;
              iVar3 = 0;
            }
          }
          else {
            iVar3 = FUN_0046cacc(param_2,DAT_005abc54);
            if (iVar3 == 0) {
              *(char *)(param_1 + 0x15) = (char)*param_3;
              iVar3 = 0;
            }
            else {
              iVar3 = 0xc;
            }
          }
        }
      }
    }
  }
  return CONCAT44(local_20,iVar3);
}

