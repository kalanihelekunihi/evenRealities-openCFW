
undefined4 FUN_0041f918(byte param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_44;
  undefined4 local_40;
  undefined1 local_1c;
  
  FUN_00415ff4(&local_50,0x38);
  iVar1 = DAT_0041f9c8;
  if (param_1 < 4) {
    if (*(char *)((uint)param_1 * 0x1c + DAT_0041f9c8 + 0x18) == '\x01') {
      local_1c = 0;
      local_44 = 0;
      local_40 = 0;
      *(undefined1 *)((uint)param_1 * 0x1c + DAT_0041f9c8 + 0x19) = 0;
      local_50 = param_2;
      local_4c = param_3;
      iVar3 = FUN_004233e8(*(undefined4 *)((uint)param_1 * 0x1c + iVar1 + 4),&local_50);
      uVar4 = 0;
      while ((uVar4 < 1000 && (*(char *)((uint)param_1 * 0x1c + iVar1 + 0x19) != '\x01'))) {
        FUN_0041f9e6(10);
        uVar4 = uVar4 + 1;
      }
      if (iVar3 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = 1;
      }
    }
    else {
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

