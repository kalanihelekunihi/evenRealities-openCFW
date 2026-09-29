
void FUN_0055f5fe(int *param_1,int param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 local_18;
  
  local_18 = param_4;
  if (*(char *)(*param_1 + 0xcd) != '\0') {
    uVar2 = FUN_0058ea08(*param_1,0);
    iVar3 = FUN_0058ea68(uVar2,1,&local_18);
    iVar1 = DAT_0055f730;
    if (iVar3 != DAT_0055f730) {
      return;
    }
    iVar3 = FUN_0058ea68(uVar2,0,(int)&local_18 + 1);
    if (iVar3 != iVar1) {
      return;
    }
    param_1[2] = local_18 & 0xffff;
  }
  *(int *)(param_2 + 4) = param_1[2];
  FUN_0055f32a(param_1,param_2);
  return;
}

