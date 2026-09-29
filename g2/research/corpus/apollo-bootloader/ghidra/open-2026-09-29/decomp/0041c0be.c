
undefined1 FUN_0041c0be(uint *param_1,uint param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined1 uVar2;
  uint *local_18;
  uint local_14;
  undefined4 uStack_10;
  uint local_c;
  
  uVar2 = 1;
  local_18 = param_1;
  local_14 = param_2;
  uStack_10 = param_3;
  local_c = param_4;
  iVar1 = FUN_0041b8f8(&local_18,(uint)param_1 & 0xff);
  if (iVar1 == 0) {
    if (local_c == 0x1e) {
      if (((*local_18 & 0x1e) != 0) && ((*local_18 & local_14) == 0)) {
        uVar2 = 0;
      }
    }
    else if (local_c == 0xc0) {
      if (((*local_18 & 0xc0) != 0) && ((*local_18 & local_14) == 0)) {
        uVar2 = 0;
      }
    }
    else if (local_c == 0x1e0) {
      if (((*local_18 & 0x1e0) != 0) && ((*local_18 & local_14) == 0)) {
        uVar2 = 0;
      }
    }
    else if (local_c == 0x1e00) {
      if (((*local_18 & 0x1e00) != 0) && ((*local_18 & local_14) == 0)) {
        uVar2 = 0;
      }
    }
    else if (local_c == DAT_0041cb00) {
      if (((*local_18 & DAT_0041cb00) != 0) && ((*local_18 & local_14) == 0)) {
        uVar2 = 0;
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

