
undefined8 FUN_00489dbc(int param_1,int *param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 uVar2;
  byte bVar3;
  int local_18;
  undefined4 uStack_14;
  
  bVar3 = 0;
  *param_2 = *param_2 + -1;
  local_18 = param_3;
  uStack_14 = param_4;
  do {
    if (3 < bVar3) {
      uVar2 = 0;
      goto LAB_00489e0e;
    }
    cVar1 = (*(code *)*DAT_00489ec4)(*param_2 + param_1);
    if (cVar1 == '\0') {
      if (*param_2 == 0) {
        uVar2 = 0;
        goto LAB_00489e0e;
      }
      *param_2 = *param_2 + -1;
    }
    bVar3 = bVar3 + 1;
  } while (cVar1 == '\0');
  local_18 = *param_2;
  uVar2 = (*(code *)*DAT_00489eac)(param_1,&local_18);
LAB_00489e0e:
  return CONCAT44(local_18,uVar2);
}

