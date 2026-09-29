
undefined8 FUN_00489e14(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  
  uVar4 = 0;
  for (iVar3 = 0; (uVar4 < param_2 && (*(char *)(param_1 + iVar3) != '\0')); iVar3 = uVar2 + iVar3)
  {
    bVar1 = (*(code *)*DAT_00489ec4)(param_1 + iVar3);
    if (bVar1 == 0) {
      uVar2 = 1;
    }
    else {
      uVar2 = (uint)bVar1;
    }
    uVar4 = uVar4 + 1;
  }
  return CONCAT44(param_4,iVar3);
}

