
void FUN_005e1bde(int param_1,int *param_2,int *param_3,int *param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int local_1a0;
  int local_19c;
  int local_198;
  int local_194;
  int local_190;
  int local_18c;
  undefined4 local_188;
  int local_184;
  int *piStack_18;
  
  piStack_18 = param_4;
  local_1a0 = *param_4 << 2;
  local_19c = param_4[1] << 2;
  local_198 = *param_3 << 2;
  local_194 = param_3[1] << 2;
  local_190 = *param_2 << 2;
  local_18c = param_2[1] << 2;
  local_188 = *(undefined4 *)(param_1 + 0xb4);
  local_184 = *(int *)(param_1 + 0xb8);
  iVar4 = (param_3[1] << 2) >> 8;
  iVar3 = (param_2[1] << 2) >> 8;
  iVar6 = *(int *)(param_1 + 0xb8) >> 8;
  if (((((*(int *)(param_1 + 0x94) <= local_19c >> 8) && (*(int *)(param_1 + 0x94) <= iVar4)) &&
       (*(int *)(param_1 + 0x94) <= iVar3)) && (*(int *)(param_1 + 0x94) <= iVar6)) ||
     (((piVar5 = &local_1a0, local_19c >> 8 < *(int *)(param_1 + 0x90) &&
       (piVar5 = &local_1a0, iVar4 < *(int *)(param_1 + 0x90))) &&
      ((piVar5 = &local_1a0, iVar3 < *(int *)(param_1 + 0x90) &&
       (piVar5 = &local_1a0, iVar6 < *(int *)(param_1 + 0x90))))))) {
    *(int *)(param_1 + 0xb4) = *param_4 << 2;
    *(int *)(param_1 + 0xb8) = local_19c;
    return;
  }
  do {
    while( true ) {
      iVar3 = piVar5[6] - *piVar5;
      iVar6 = piVar5[7] - piVar5[1];
      iVar4 = iVar3;
      if (iVar3 < 0) {
        iVar4 = -iVar3;
      }
      iVar7 = iVar6;
      if (iVar6 < 0) {
        iVar7 = -iVar6;
      }
      if (iVar7 < iVar4) {
        iVar4 = iVar4 + (iVar7 * 3 >> 3);
      }
      else {
        iVar4 = iVar7 + (iVar4 * 3 >> 3);
      }
      if (iVar4 < 0x8000) break;
LAB_005e1cc4:
      FUN_005e1b4c(piVar5);
      piVar5 = piVar5 + 6;
    }
    iVar7 = piVar5[2] - *piVar5;
    iVar8 = piVar5[3] - piVar5[1];
    if (iVar7 * iVar6 - iVar8 * iVar3 < 0) {
      iVar1 = iVar8 * iVar3 - iVar7 * iVar6;
    }
    else {
      iVar1 = iVar7 * iVar6 - iVar8 * iVar3;
    }
    if (iVar4 * 0x2a < iVar1) goto LAB_005e1cc4;
    iVar1 = piVar5[4] - *piVar5;
    iVar9 = piVar5[5] - piVar5[1];
    if (iVar1 * iVar6 - iVar9 * iVar3 < 0) {
      iVar2 = iVar9 * iVar3 - iVar1 * iVar6;
    }
    else {
      iVar2 = iVar1 * iVar6 - iVar9 * iVar3;
    }
    if (((iVar4 * 0x2a < iVar2) || (0 < (iVar7 - iVar3) * iVar7 + (iVar8 - iVar6) * iVar8)) ||
       (0 < (iVar1 - iVar3) * iVar1 + (iVar9 - iVar6) * iVar9)) goto LAB_005e1cc4;
    FUN_005e17c2(param_1,*piVar5,piVar5[1]);
    if (piVar5 == &local_1a0) {
      return;
    }
    piVar5 = piVar5 + -6;
  } while( true );
}

