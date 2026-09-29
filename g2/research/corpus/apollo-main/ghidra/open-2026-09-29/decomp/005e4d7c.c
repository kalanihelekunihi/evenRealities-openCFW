
undefined8 FUN_005e4d7c(int param_1,int param_2,int param_3,int param_4)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if ((param_1 == 0) || (*(int *)(param_1 + 0x214) == 0)) {
    uVar2 = 0;
  }
  else if ((param_2 == 0x45) && (*(char *)(param_1 + 0x27c) != '\0')) {
    iVar3 = FUN_0044e498(*(undefined4 *)(param_1 + 0x214));
    iVar4 = FUN_0044e4bc(*(undefined4 *)(param_1 + 0x214));
    if (((param_3 < param_4) && (iVar5 = FUN_005eb576(2,param_3), iVar5 == 0)) &&
       (0 < iVar4 + iVar3)) {
      bVar1 = 0;
    }
    else {
      bVar1 = 1;
    }
    uVar2 = (uint)bVar1;
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(param_4,uVar2);
}

