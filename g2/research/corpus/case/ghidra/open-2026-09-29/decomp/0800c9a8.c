
undefined4
xTaskCreate(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4,undefined4 param_5,
           undefined4 param_6)

{
  int iVar1;
  int iVar2;
  
  iVar1 = pvPortMalloc(param_3 << 2);
  if (iVar1 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = pvPortMalloc(0x5c);
    if (iVar2 == 0) {
      FUN_0800c030(iVar1);
    }
    else {
      *(int *)(iVar2 + 0x30) = iVar1;
    }
  }
  if (iVar2 != 0) {
    *(undefined1 *)(iVar2 + 0x59) = 0;
    FUN_0800ae96(param_1,param_2,param_3,param_4,param_5,param_6,iVar2,0);
    FUN_0800ac08(iVar2);
    return 1;
  }
  return 0xffffffff;
}

