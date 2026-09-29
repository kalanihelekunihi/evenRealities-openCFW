
undefined4 FUN_00550334(int param_1)

{
  int *piVar1;
  int iVar2;
  undefined1 local_28;
  undefined1 local_27;
  undefined1 local_26;
  undefined1 local_25;
  undefined1 local_24;
  undefined1 local_23;
  undefined1 local_20;
  undefined1 local_1f;
  undefined1 local_1e;
  undefined1 local_1d;
  undefined1 local_1c;
  undefined1 local_1b;
  undefined1 local_18;
  undefined1 local_17;
  undefined1 local_16;
  undefined1 local_15;
  undefined1 local_14;
  undefined1 local_13;
  undefined1 local_10;
  undefined1 local_f;
  undefined1 local_e;
  undefined1 local_d;
  undefined1 local_c;
  undefined1 local_b;
  
  if (param_1 == 10) {
    local_20 = 3;
    local_1f = 10;
    local_1e = 0;
    local_1d = 0;
    local_1c = 0;
    local_1b = 0;
    FUN_00464bb2(4,&local_20,6,0);
  }
  else if (param_1 == 0x48) {
    local_28 = 3;
    local_27 = 0x48;
    local_26 = 0;
    local_25 = 0;
    local_24 = 0;
    local_23 = 0;
    FUN_00464bb2(4,&local_28,6,0);
  }
  else if (param_1 == 0x45) {
    if (*DAT_00550d38 == '\0') {
      if (*DAT_00550f7c < 1) {
        *DAT_00550f7c = 0;
      }
      local_10 = 3;
      local_f = 0x45;
      local_e = 1;
      local_d = 0;
      local_c = 0;
      local_b = 0;
      FUN_00464bb2(4,&local_10,6,0);
    }
  }
  else if ((param_1 == 0x44) && (*DAT_00550d38 == '\0')) {
    iVar2 = FUN_005511bc();
    piVar1 = DAT_00550f7c;
    if (iVar2 < *DAT_00550f7c) {
      iVar2 = FUN_005511bc();
      *piVar1 = iVar2;
    }
    local_18 = 3;
    local_17 = 0x44;
    local_16 = 1;
    local_15 = 0;
    local_14 = 0;
    local_13 = 0;
    FUN_00464bb2(4,&local_18,6,0);
  }
  return 0;
}

