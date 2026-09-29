
uint FUN_00508954(undefined4 param_1)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  char local_40 [2];
  undefined2 local_3e;
  undefined4 local_3c;
  undefined1 auStack_38 [13];
  undefined1 local_2b;
  undefined1 auStack_28 [4];
  code *local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  
  *DAT_00508a70 = param_1;
  FUN_0055d280(param_1);
  FUN_0050649a(param_1,0,auStack_38);
  local_2b = 1;
  FUN_0050637c(param_1,0,auStack_38);
  uVar1 = DAT_00508a84;
  local_24 = DAT_00508a7c;
  local_20 = DAT_00508a80;
  local_1c = 0x15;
  local_18 = 6;
  FUN_0055d644(DAT_00508a84,auStack_28);
  uVar2 = FUN_0055d67a(uVar1);
  if ((uVar2 == 0) && (uVar2 = FUN_0055d666(uVar1,local_40), uVar2 == 0)) {
    if (local_40[0] == 'E') {
      *DAT_00508a88 = 0x45;
      *DAT_00508a8c = 1;
      uVar3 = (*local_24)(uVar1,6,local_40,1);
      uVar4 = FUN_0050649a(param_1,0,auStack_38);
      local_2b = 0;
      uVar2 = FUN_0050637c(param_1,0,auStack_38);
      uVar2 = uVar3 | uVar4 | uVar2;
      local_3e = *DAT_00508a90;
      local_3c = *DAT_00508a94;
      local_40[1] = 0x82;
      FUN_00508e74(param_1,0xa20e,2,&local_3e);
      FUN_00508e74(param_1,0xa233,4,&local_3c);
      FUN_00508e74(param_1,0xa207,1,local_40 + 1);
    }
    else {
      uVar2 = 0xffffffff;
    }
  }
  return uVar2;
}

