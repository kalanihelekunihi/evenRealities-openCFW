
undefined8 FUN_004cad80(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_004cad76(param_1);
  iVar2 = FUN_00541b52(param_1 + iVar1,&DAT_004cada8);
  return CONCAT44(param_4,(uint)(*(char *)(param_1 + iVar2 + iVar1) == '\0'));
}

