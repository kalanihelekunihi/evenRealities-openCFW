
undefined4 FT_Match_Size(int param_1,char *param_2,char param_3,int *param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  if ((int)((uint)*(byte *)(param_1 + 8) << 0x1e) < 0) {
    if (*param_2 == '\0') {
      if (*(int *)(param_2 + 0xc) == 0) {
        iVar2 = *(int *)(param_2 + 4);
      }
      else {
        iVar2 = (*(int *)(param_2 + 0xc) * *(int *)(param_2 + 4) + 0x24) / 0x48;
      }
      if (*(int *)(param_2 + 0x10) == 0) {
        iVar4 = *(int *)(param_2 + 8);
      }
      else {
        iVar4 = (*(int *)(param_2 + 0x10) * *(int *)(param_2 + 8) + 0x24) / 0x48;
      }
      if ((((*(int *)(param_2 + 4) == 0) || (iVar5 = iVar2, *(int *)(param_2 + 8) != 0)) &&
          (iVar5 = iVar4, *(int *)(param_2 + 4) == 0)) && (*(int *)(param_2 + 8) != 0)) {
        iVar2 = iVar4;
      }
      uVar3 = iVar2 + 0x20U & 0xffffffc0;
      uVar6 = iVar5 + 0x20U & 0xffffffc0;
      if ((uVar3 == 0) || (uVar6 == 0)) {
        uVar1 = 0x17;
      }
      else {
        for (iVar2 = 0; iVar2 < *(int *)(param_1 + 0x1c); iVar2 = iVar2 + 1) {
          iVar4 = *(int *)(param_1 + 0x20) + iVar2 * 0x10;
          if ((uVar6 == (*(int *)(iVar4 + 0xc) + 0x20U & 0xffffffc0)) &&
             ((uVar3 == (*(int *)(iVar4 + 8) + 0x20U & 0xffffffc0) || (param_3 != '\0')))) {
            if (param_4 != (int *)0x0) {
              *param_4 = iVar2;
            }
            return 0;
          }
        }
        uVar1 = 0x17;
      }
    }
    else {
      uVar1 = 7;
    }
  }
  else {
    uVar1 = 0x23;
  }
  return uVar1;
}

