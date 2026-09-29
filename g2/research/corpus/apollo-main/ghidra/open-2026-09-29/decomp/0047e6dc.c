
undefined8
FUN_0047e6dc(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_3;
  iVar1 = pvPortMalloc(0x2c);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 0x28) = 0;
    FUN_0047e75a(param_1,param_2,param_3,param_4,param_5,iVar1);
    uVar2 = param_5;
  }
  return CONCAT44(uVar2,iVar1);
}

