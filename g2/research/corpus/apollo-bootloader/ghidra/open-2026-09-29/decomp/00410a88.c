
undefined8 FUN_00410a88(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_00410a7e(param_1);
  iVar2 = FUN_0041581a(param_1 + iVar1,&DAT_00410ab0);
  return CONCAT44(param_4,(uint)(*(char *)(param_1 + iVar2 + iVar1) == '\0'));
}

