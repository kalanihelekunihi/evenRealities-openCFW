
undefined8 FUN_0053f42a(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  byte bVar2;
  byte bVar3;
  uint uVar4;
  uint uVar5;
  undefined4 local_18;
  
  if (((*(byte *)(param_2 + 0x51) & 7) == 2) || ((*(byte *)(param_2 + 0x51) & 7) == 3)) {
    local_18 = DAT_0053fa64;
    FUN_0044d25c(2,DAT_0053fa6c,0x4a,DAT_0053fa68);
  }
  else {
    if ((((*(int *)(param_2 + 0x30) == 0) && (*(int *)(param_2 + 0x34) == 0x100)) &&
        (*(int *)(param_2 + 0x38) == 0x100)) &&
       ((*(int *)(param_2 + 0x40) == 0 && (*(int *)(param_2 + 0x3c) == 0)))) {
      bVar1 = false;
    }
    else {
      bVar1 = true;
    }
    local_18 = param_3;
    if ((*(ushort *)(param_2 + 0x50) & 0x1fff) >> 0xc != 0) {
      if (bVar1) {
        local_18 = DAT_0053fa70;
        FUN_0044d25c(2,DAT_0053fa6c,0x55,DAT_0053fa68);
      }
      uVar4 = *(uint *)(param_2 + 0x24) & 0xffff;
      uVar5 = *(uint *)(param_2 + 0x24) >> 0x10;
      if ((uVar4 == 0) || ((uVar4 & uVar4 - 1) != 0)) {
        bVar3 = 0;
      }
      else {
        bVar3 = 1;
      }
      if ((uVar5 == 0) || ((uVar5 & uVar5 - 1) != 0)) {
        bVar2 = 0;
      }
      else {
        bVar2 = 1;
      }
      if (!(bool)(bVar3 & bVar2)) {
        local_18 = DAT_0053fa74;
        FUN_0044d25c(2,DAT_0053fa6c,0x60,DAT_0053fa68);
      }
      if (*(int *)(param_2 + 0x2c) != 0) {
        local_18 = DAT_0053fa78;
        FUN_0044d25c(2,DAT_0053fa6c,0x65,DAT_0053fa68);
      }
      if (*(int *)(param_2 + 0x68) != 0) {
        local_18 = DAT_0053fa7c;
        FUN_0044d25c(2,DAT_0053fa6c,0x6a,DAT_0053fa68);
      }
    }
    FUN_0053f548(param_1,param_2,param_3);
  }
  return CONCAT44(param_4,local_18);
}

