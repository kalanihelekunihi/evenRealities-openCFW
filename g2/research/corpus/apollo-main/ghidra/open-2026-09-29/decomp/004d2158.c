
int FUN_004d2158(code *param_1,undefined4 *param_2,int param_3)

{
  bool bVar1;
  int iVar2;
  char *pcVar3;
  uint uVar4;
  int iVar5;
  undefined1 *unaff_r4;
  undefined1 *puVar6;
  char *unaff_r5;
  int iVar7;
  uint unaff_r9;
  int local_30;
  
  iVar7 = 0;
  bVar1 = false;
  if (param_3 < 0) {
    iVar2 = param_2[2];
    param_2[2] = (char *)(iVar2 + 1);
    if (*(char *)(iVar2 + 1) == '^') {
      param_2[2] = iVar2 + 2;
      unaff_r9 = (uint)*(byte *)(iVar2 + 1);
    }
    else {
      unaff_r9 = 0;
    }
    unaff_r5 = (char *)param_2[2];
    pcVar3 = unaff_r5;
    if (*unaff_r5 == ']') {
      pcVar3 = unaff_r5 + 1;
    }
    iVar2 = FUN_00481818(pcVar3,0x5d);
    if (iVar2 != 0) {
      local_30 = iVar2 - (int)unaff_r5;
      param_2[2] = iVar2;
      if ((2 < local_30) && (iVar2 = FUN_004d40e0(unaff_r5 + 1,0x2d,local_30 + -2), iVar2 != 0)) {
        bVar1 = true;
      }
      goto LAB_004d21bc;
    }
LAB_004d22ec:
    iVar7 = 0;
  }
  else {
LAB_004d21bc:
    iVar2 = param_2[5];
    if (iVar2 < 1) {
      if (param_3 == 0) {
        iVar2 = 1;
      }
      else {
        iVar2 = 0x7fffffff;
      }
    }
    param_2[4] = iVar2;
    if (*(char *)(param_2 + 7) == '\0') {
      unaff_r4 = *(undefined1 **)param_2[1];
      param_2[1] = (undefined4 *)param_2[1] + 1;
    }
    if (*(char *)(param_2 + 7) == '\0' && unaff_r4 == (undefined1 *)0x0) {
      pcVar3 = (char *)((int)&DAT_004d21f0 + DAT_004d21f0);
LAB_004d2212:
      iVar7 = FUN_004d40a0(pcVar3);
      return -1 - iVar7;
    }
    if ((*(char *)(param_2 + 7) == '\0') && (*(char *)((int)param_2 + 0x1f) != '\0')) {
      uVar4 = *(uint *)param_2[1];
      param_2[1] = (uint *)param_2[1] + 1;
      if (0x7fffffff < uVar4) {
        pcVar3 = s_scanf_s__bad__c___s__or____size_004d2324;
        goto LAB_004d2212;
      }
      if ((uint)param_2[6] < uVar4) {
        uVar4 = param_2[6];
      }
      param_2[6] = uVar4;
    }
    while( true ) {
      iVar2 = param_2[4];
      param_2[4] = iVar2 + -1;
      param_2[3] = param_2[3] + 1;
      if (iVar2 + -1 < 0) break;
      iVar2 = (*param_1)(*param_2,0,1);
      if (iVar2 == -1) goto LAB_004d22bc;
      if (0 < param_3) {
        iVar5 = FUN_004d58ae();
        goto LAB_004d228e;
      }
      if (param_3 < 0) {
        if (bVar1) {
          if (unaff_r9 == 0) {
            iVar5 = FUN_004d2112(unaff_r5,iVar2,local_30);
joined_r0x004d2296:
            if (iVar5 != 0) goto LAB_004d22a0;
            goto LAB_004d22bc;
          }
          iVar5 = FUN_004d2112(unaff_r5,iVar2,local_30);
        }
        else {
          if (unaff_r9 == 0) {
            iVar5 = FUN_004d40e0(unaff_r5,iVar2,local_30);
            goto joined_r0x004d2296;
          }
          iVar5 = FUN_004d40e0(unaff_r5,iVar2,local_30);
        }
LAB_004d228e:
        if (iVar5 != 0) goto LAB_004d22bc;
      }
LAB_004d22a0:
      puVar6 = unaff_r4;
      if (*(char *)(param_2 + 7) == '\0') {
        if (param_2[6] == 0) {
          iVar7 = 1;
          goto LAB_004d22bc;
        }
        puVar6 = unaff_r4 + 1;
        *unaff_r4 = (char)iVar2;
        *(undefined1 *)((int)param_2 + 0x1e) = 1;
        param_2[6] = param_2[6] + -1;
      }
      iVar7 = 2;
      unaff_r4 = puVar6;
    }
    iVar2 = -1;
LAB_004d22bc:
    FUN_004d161c(param_1,param_2,iVar2);
    if ((param_3 == 0) || (iVar7 != 2)) {
      if (iVar7 != 2) {
        if ((iVar7 << 0x1f < 0) || (iVar2 == -1)) {
          return -1;
        }
        goto LAB_004d22ec;
      }
    }
    else if (*(char *)(param_2 + 7) == '\0') {
      if (param_2[6] == 0) goto LAB_004d22ec;
      *unaff_r4 = 0;
    }
    iVar7 = 1;
  }
  return iVar7;
}

