
undefined4 address_validate_430a60(uint param_1,uint param_2)

{
  uint *puVar1;
  undefined4 uVar2;
  undefined1 auStack_50 [44];
  uint uStack_24;
  
  puVar1 = DAT_00430b0c;
  if (*DAT_00430b0c == 0) {
    FUN_0041d792(1,auStack_50);
    *puVar1 = uStack_24;
  }
  if (param_1 < 0x4000) {
    uVar2 = 0;
  }
  else if (param_2 < *puVar1) {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

