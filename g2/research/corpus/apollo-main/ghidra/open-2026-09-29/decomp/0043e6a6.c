
undefined8 FUN_0043e6a6(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  byte bVar2;
  undefined4 uVar3;
  undefined4 local_10;
  
  local_10 = param_4;
  FUN_00451b9c(param_2);
  uVar1 = FUN_0043dda8(param_1,0x10000);
  *(undefined1 *)(param_2 + 0x20) = uVar1;
  if (2 < *(byte *)(param_2 + 0x20)) {
    local_10 = FUN_0043dd9a(param_1,0x10000);
    FUN_00439be4(param_2 + 0x21,&local_10,3);
  }
  uVar1 = FUN_0043ddf0(param_1,0x10000);
  *(undefined1 *)(param_2 + 0x48) = uVar1;
  if (2 < *(byte *)(param_2 + 0x48)) {
    uVar3 = FUN_0043ddfc(param_1,0x10000);
    *(undefined4 *)(param_2 + 0x44) = uVar3;
    if (*(int *)(param_2 + 0x44) < 1) {
      *(undefined1 *)(param_2 + 0x48) = 0;
    }
    else {
      local_10 = FUN_0043dde2(param_1,0x10000);
      FUN_00439be4(param_2 + 0x3e,&local_10,3);
    }
  }
  uVar1 = FUN_0043de3e(param_1,0x10000);
  *(undefined1 *)(param_2 + 0x6c) = uVar1;
  if (2 < *(byte *)(param_2 + 0x6c)) {
    uVar3 = FUN_0043de1c(param_1,0x10000);
    *(undefined4 *)(param_2 + 0x5c) = uVar3;
    if (*(int *)(param_2 + 0x5c) < 1) {
      *(undefined1 *)(param_2 + 0x6c) = 0;
    }
    else {
      uVar3 = FUN_0043de26(param_1,0x10000);
      *(undefined4 *)(param_2 + 0x68) = uVar3;
      local_10 = FUN_0043de30(param_1,0x10000);
      FUN_00439be4(param_2 + 0x59,&local_10,3);
    }
  }
  bVar2 = FUN_0044c47a(param_1,0x10000);
  if (bVar2 < 0xfd) {
    uVar1 = (undefined1)((uint)bVar2 * (uint)*(byte *)(param_2 + 0x20) >> 8);
    *(undefined1 *)(param_2 + 0x20) = uVar1;
    *(undefined1 *)(param_2 + 0x48) = uVar1;
    *(undefined1 *)(param_2 + 0x6c) = uVar1;
  }
  if (((*(char *)(param_2 + 0x20) == '\0') && (*(char *)(param_2 + 0x48) == '\0')) &&
     (*(char *)(param_2 + 0x6c) == '\0')) {
    uVar3 = 0;
  }
  else {
    uVar3 = FUN_0043de4a(param_1,0x10000);
    *(undefined4 *)(param_2 + 0x1c) = uVar3;
    uVar3 = 1;
  }
  return CONCAT44(local_10,uVar3);
}

