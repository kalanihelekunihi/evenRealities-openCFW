
undefined8 FUN_00490fa2(int param_1,int param_2)

{
  undefined4 uVar1;
  ushort *puVar2;
  undefined4 unaff_r7;
  
  puVar2 = *(ushort **)(param_2 + 0x1c);
  if (puVar2 == (ushort *)0x0) {
    uVar1 = FUN_00490db6(param_1,0,0);
  }
  else if (((*(byte *)(param_2 + 0x16) & 0xc0) == 0) &&
          (*(ushort *)(param_2 + 0x12) - 2 < (uint)*puVar2)) {
    uVar1 = DAT_004910d8;
    if (*(int *)(param_1 + 0x10) != 0) {
      uVar1 = *(undefined4 *)(param_1 + 0x10);
    }
    *(undefined4 *)(param_1 + 0x10) = uVar1;
    uVar1 = 0;
  }
  else {
    uVar1 = FUN_00490db6(param_1,puVar2 + 1,*puVar2);
  }
  return CONCAT44(unaff_r7,uVar1);
}

