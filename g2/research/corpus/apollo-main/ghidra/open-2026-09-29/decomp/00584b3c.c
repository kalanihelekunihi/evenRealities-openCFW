
int FUN_00584b3c(uint param_1,char param_2)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  int local_18;
  
  piVar1 = DAT_00584e68;
  local_18 = 0;
  uVar3 = 0x400 - *DAT_00584e68;
  if (uVar3 < param_1) {
    if ((*DAT_00584e68 != 0) && (*DAT_00584e6c != 0)) {
      (*(code *)*DAT_00584e6c)(DAT_00584e70,*DAT_00584e68);
    }
    *piVar1 = 0;
    uVar3 = 0x400;
  }
  iVar2 = DAT_00584e70;
  if (uVar3 < param_1) {
    param_1 = uVar3;
  }
  FUN_0058e2d8(*DAT_00584e48,DAT_00584e70 + *piVar1,param_1,&local_18);
  *piVar1 = local_18 + *piVar1;
  if (param_2 != '\0') {
    if ((*DAT_00584e6c != 0) && (*piVar1 != 0)) {
      (*(code *)*DAT_00584e6c)(iVar2,*piVar1);
    }
    *piVar1 = 0;
  }
  return local_18;
}

