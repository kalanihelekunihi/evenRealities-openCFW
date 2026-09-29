
undefined4
FUN_004548ba(undefined4 param_1,undefined4 param_2,ushort param_3,undefined4 param_4,
            undefined4 param_5,undefined4 param_6)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = pvPortMalloc((uint)param_3 << 2);
  if (iVar1 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = pvPortMalloc(0x70);
    if (iVar2 == 0) {
      vPortFree(iVar1);
    }
    else {
      FUN_0043c0e4(iVar2,0x70,0);
      *(int *)(iVar2 + 0x30) = iVar1;
    }
  }
  if (iVar2 == 0) {
    uVar3 = 0xffffffff;
  }
  else {
    *(undefined1 *)(iVar2 + 0x6d) = 0;
    FUN_00454938(param_1,param_2,param_3,param_4,param_5,param_6,iVar2,0);
    FUN_004549fc(iVar2);
    uVar3 = 1;
  }
  return uVar3;
}

