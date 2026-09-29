
undefined8 FUN_005caf94(undefined4 param_1,int param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  undefined1 uVar2;
  byte bVar3;
  undefined4 uVar4;
  int local_18;
  undefined4 local_14;
  
  local_18 = param_3;
  local_14 = param_4;
  if (param_3 == 0) {
    local_14 = FUN_005c9e36(param_1,0);
    FUN_00439be4(param_2 + 0x1c,&local_14,3);
    uVar2 = FUN_005c9e44(param_1,0);
    *(undefined1 *)(param_2 + 0x3c) = uVar2;
    uVar4 = FUN_005c9e16(param_1,0);
    *(undefined4 *)(param_2 + 0x20) = uVar4;
    bVar3 = FUN_005c9e20(param_1,0);
    *(byte *)(param_2 + 0x3d) = *(byte *)(param_2 + 0x3d) & 0xfe | bVar3 & 1;
    uVar4 = FUN_005c9e50(param_1,0);
    *(undefined4 *)(param_2 + 0x38) = uVar4;
  }
  else {
    cVar1 = FUN_00482946(param_3,0x50,&local_18);
    if (cVar1 == '\x01') {
      *(int *)(param_2 + 0x20) = local_18;
    }
    else {
      uVar4 = FUN_005c9e16(param_1,0);
      *(undefined4 *)(param_2 + 0x20) = uVar4;
    }
    cVar1 = FUN_00482946(param_3,0x52,&local_18);
    if (cVar1 == '\x01') {
      FUN_00439be4(param_2 + 0x1c,&local_18,3);
    }
    else {
      local_14 = FUN_005c9e36(param_1,0);
      FUN_00439be4(param_2 + 0x1c,&local_14,3);
    }
    cVar1 = FUN_00482946(param_3,0x53,&local_18);
    if (cVar1 == '\x01') {
      *(char *)(param_2 + 0x3c) = (char)local_18;
    }
    else {
      uVar2 = FUN_005c9e44(param_1,0);
      *(undefined1 *)(param_2 + 0x3c) = uVar2;
    }
    cVar1 = FUN_00482946(param_3,0x51,&local_18);
    if (cVar1 == '\x01') {
      *(byte *)(param_2 + 0x3d) = *(byte *)(param_2 + 0x3d) & 0xfe | (byte)local_18 & 1;
    }
    else {
      bVar3 = FUN_005c9e20(param_1,0);
      *(byte *)(param_2 + 0x3d) = *(byte *)(param_2 + 0x3d) & 0xfe | bVar3 & 1;
    }
    cVar1 = FUN_00482946(param_3,0x54,&local_18);
    if (cVar1 == '\x01') {
      *(int *)(param_2 + 0x38) = local_18;
    }
    else {
      uVar4 = FUN_005c9e50(param_1,0);
      *(undefined4 *)(param_2 + 0x38) = uVar4;
    }
  }
  return CONCAT44(local_14,local_18);
}

