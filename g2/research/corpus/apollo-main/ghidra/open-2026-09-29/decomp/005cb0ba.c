
undefined8 FUN_005cb0ba(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  int local_18;
  undefined4 local_14;
  
  local_18 = param_3;
  local_14 = param_4;
  if (param_3 == 0) {
    local_14 = FUN_005c9e5a(param_1,0x20000);
    FUN_00439be4(param_2 + 0x24,&local_14,3);
    uVar2 = FUN_005c9e68(param_1,0x20000);
    *(undefined1 *)(param_2 + 0x50) = uVar2;
    uVar3 = FUN_005c9e7e(param_1,0x20000);
    *(undefined4 *)(param_2 + 0x2c) = uVar3;
    uVar3 = FUN_005c9e74(param_1,0x20000);
    *(undefined4 *)(param_2 + 0x20) = uVar3;
  }
  else {
    cVar1 = FUN_00482946(param_3,0x58,&local_18);
    if (cVar1 == '\x01') {
      FUN_00439be4(param_2 + 0x24,&local_18,3);
    }
    else {
      local_14 = FUN_005c9e5a(param_1,0x20000);
      FUN_00439be4(param_2 + 0x24,&local_14,3);
    }
    cVar1 = FUN_00482946(param_3,0x59,&local_18);
    if (cVar1 == '\x01') {
      *(char *)(param_2 + 0x50) = (char)local_18;
    }
    else {
      uVar2 = FUN_005c9e68(param_1,0x20000);
      *(undefined1 *)(param_2 + 0x50) = uVar2;
    }
    cVar1 = FUN_00482946(param_3,0x5b,&local_18);
    if (cVar1 == '\x01') {
      *(int *)(param_2 + 0x2c) = local_18;
    }
    else {
      uVar3 = FUN_005c9e7e(param_1,0x20000);
      *(undefined4 *)(param_2 + 0x2c) = uVar3;
    }
    cVar1 = FUN_00482946(param_3,0x5a,&local_18);
    if (cVar1 == '\x01') {
      *(int *)(param_2 + 0x20) = local_18;
    }
    else {
      uVar3 = FUN_005c9e74(param_1,0x20000);
      *(undefined4 *)(param_2 + 0x20) = uVar3;
    }
  }
  return CONCAT44(local_14,local_18);
}

