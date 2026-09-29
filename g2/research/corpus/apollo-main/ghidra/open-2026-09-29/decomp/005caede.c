
undefined8 FUN_005caede(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  int local_20;
  int local_1c;
  undefined4 uStack_18;
  
  local_20 = param_2;
  local_1c = param_3;
  uStack_18 = param_4;
  if (param_3 == 0) {
    local_1c = FUN_005c9dfc(param_1,param_4);
    FUN_00439be4(param_2 + 0x2c,&local_1c,3);
    uVar2 = FUN_005c9e0a(param_1,param_4);
    *(undefined1 *)(param_2 + 0x3c) = uVar2;
    uVar3 = FUN_005c9df2(param_1,param_4);
    *(undefined4 *)(param_2 + 0x30) = uVar3;
  }
  else {
    cVar1 = FUN_00482946(param_3,0x48,&local_20);
    if (cVar1 == '\x01') {
      *(int *)(param_2 + 0x30) = local_20;
    }
    else {
      uVar3 = FUN_005c9df2(param_1,param_4);
      *(undefined4 *)(param_2 + 0x30) = uVar3;
    }
    cVar1 = FUN_00482946(param_3,0x4c,&local_20);
    if (cVar1 == '\x01') {
      FUN_00439be4(param_2 + 0x2c,&local_20,3);
    }
    else {
      local_1c = FUN_005c9dfc(param_1,param_4);
      FUN_00439be4(param_2 + 0x2c,&local_1c,3);
    }
    cVar1 = FUN_00482946(param_3,0x4d,&local_20);
    if (cVar1 == '\x01') {
      *(char *)(param_2 + 0x3c) = (char)local_20;
    }
    else {
      uVar2 = FUN_005c9e0a(param_1,param_4);
      *(undefined1 *)(param_2 + 0x3c) = uVar2;
    }
  }
  return CONCAT44(local_1c,local_20);
}

