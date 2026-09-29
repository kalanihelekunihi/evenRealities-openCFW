
undefined8 FUN_004b202c(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_10;
  
  iVar1 = FUN_005293c0(param_2 << 1);
  if (iVar1 == 0) {
    local_10 = DAT_004b22d4;
    FUN_0044d25c(3,DAT_004b226c,0xf2,DAT_004b22d8);
    uVar2 = 0;
  }
  else {
    *(int *)(*(int *)(param_1 + 0x34) + 0x18) = iVar1;
    if (*(char *)(param_1 + 0x2d) == '\0') {
      iVar1 = FUN_005297b8(param_2);
    }
    else {
      if (*(char *)(param_1 + 0x2d) != '\x01') {
        local_10 = DAT_004b22e0;
        FUN_0044d25c(3,DAT_004b226c,0xff,DAT_004b22d8);
        uVar2 = 0;
        goto LAB_004b20a8;
      }
      iVar1 = FUN_00529b38(param_2);
    }
    if (iVar1 == 0) {
      local_10 = DAT_004b22dc;
      FUN_0044d25c(3,DAT_004b226c,0x104,DAT_004b22d8);
      uVar2 = 0;
    }
    else {
      *(int *)(*(int *)(param_1 + 0x34) + 0x1c) = iVar1;
      uVar2 = 1;
      local_10 = param_4;
    }
  }
LAB_004b20a8:
  return CONCAT44(local_10,uVar2);
}

