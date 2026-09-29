
undefined8 FUN_0053653a(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  iVar1 = *(int *)(param_1 + 0x30);
  iStack_20 = param_1;
  uStack_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  FUN_0043c0e4(&iStack_20,0x10,0);
  FUN_005363ae(iVar1 + 4,&iStack_20,param_1,*(undefined1 *)(iVar1 + 0x28));
  return CONCAT44(uStack_1c,iStack_20);
}

