
undefined8 FUN_00585bc8(undefined4 *param_1,byte param_2,uint param_3,undefined4 param_4)

{
  char *pcVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint local_18;
  
  local_18 = param_3;
  if (param_2 == 0) {
    *(undefined1 *)(param_1 + 6) = 1;
    pcVar1 = DAT_00585c78;
    uVar3 = DAT_00585c50;
    if (*DAT_00585c78 == '\0') {
      FUN_004733ee(DAT_00585c50);
      FUN_004733ee(&DAT_00585c48);
      FUN_004733ee(DAT_00585c80,DAT_00585c7c);
      FUN_004733ee(uVar3);
      FUN_004733ee(&DAT_00585c48);
      FUN_004733ee(DAT_00585c84);
      *pcVar1 = '\x01';
    }
  }
  else if (*(char *)((int)param_1 + 0x1a) == '\0') {
    FUN_004733ee(DAT_00585c50);
    FUN_004733ee(&DAT_00585c48);
    uVar2 = FUN_00585c94(param_1);
    uVar3 = DAT_00585c8c;
    if (*(char *)(param_1 + 1) == '\0') {
      uVar3 = DAT_00585c88;
    }
    local_18 = (uint)param_2;
    FUN_004733ee(DAT_00585c90,uVar3,*param_1,uVar2);
  }
  return CONCAT44(param_4,local_18);
}

