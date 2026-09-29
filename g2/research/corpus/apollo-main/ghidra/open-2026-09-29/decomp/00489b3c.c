
void FUN_00489b3c(int param_1,int *param_2,undefined4 *param_3,int *param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_00489eac;
  iVar2 = (*(code *)*DAT_00489eac)(param_1,param_4);
  *param_2 = iVar2;
  if (*param_2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar3 = (*(code *)*puVar1)(*param_4 + param_1,0);
  }
  *param_3 = uVar3;
  return;
}

