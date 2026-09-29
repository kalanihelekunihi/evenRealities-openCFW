
undefined8 FUN_0041bd92(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  uint *puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint local_10;
  undefined4 uStack_c;
  
  puVar1 = DAT_0041c4a0;
  local_10 = param_3;
  if (*DAT_0041c49c == '\x01') {
    local_10 = *DAT_0041c4a0 | 0x80;
    uStack_c = param_4;
    FUN_0041cd1a(5,1,&local_10);
    *DAT_0041c4a8 = *DAT_0041c4a8 | 0x20;
    uVar3 = 0;
    while ((uVar3 < 10000 && (-1 < (int)(*puVar1 << 0x18)))) {
      uVar3 = uVar3 + 1;
    }
    if (uVar3 == 10000) {
      uVar2 = 4;
      goto LAB_0041bde2;
    }
  }
  uVar2 = 0;
LAB_0041bde2:
  return CONCAT44(local_10,uVar2);
}

