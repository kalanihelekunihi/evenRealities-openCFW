
int af_iup_interp(uint param_1,uint param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  if (param_1 <= param_2) {
    iVar1 = param_3;
    iVar3 = param_4;
    if (*(int *)(param_4 + 0x1c) < *(int *)(param_3 + 0x1c)) {
      iVar1 = param_4;
      iVar3 = param_3;
    }
    iVar5 = *(int *)(iVar1 + 0x1c);
    iVar6 = *(int *)(iVar3 + 0x1c);
    iVar7 = *(int *)(iVar1 + 0x18);
    iVar1 = *(int *)(iVar3 + 0x18);
    if ((iVar7 == iVar1) || (iVar5 == iVar6)) {
      for (; param_1 <= param_2; param_1 = param_1 + 0x28) {
        iVar3 = *(int *)(param_1 + 0x1c);
        if (iVar5 < iVar3) {
          iVar2 = iVar7;
          if (iVar6 <= iVar3) {
            iVar2 = (iVar1 - iVar6) + iVar3;
          }
        }
        else {
          iVar2 = (iVar7 - iVar5) + iVar3;
        }
        *(int *)(param_1 + 0x18) = iVar2;
      }
    }
    else {
      uVar4 = FT_DivFix(iVar1 - iVar7,iVar6 - iVar5);
      for (; param_1 <= param_2; param_1 = param_1 + 0x28) {
        iVar3 = *(int *)(param_1 + 0x1c);
        if (iVar5 < iVar3) {
          if (iVar3 < iVar6) {
            iVar3 = FT_MulFix(iVar3 - iVar5,uVar4);
            iVar3 = iVar3 + iVar7;
          }
          else {
            iVar3 = (iVar1 - iVar6) + iVar3;
          }
        }
        else {
          iVar3 = (iVar7 - iVar5) + iVar3;
        }
        *(int *)(param_1 + 0x18) = iVar3;
      }
    }
  }
  return param_4;
}

