
undefined8 osMemoryPoolAlloc(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  uVar1 = DAT_00449e90;
  if (param_1 == 0) {
    iVar4 = 0;
  }
  else {
    iVar4 = 0;
    if ((*(uint *)(param_1 + 0x20) & DAT_00449e90) == DAT_00449e90) {
      iVar2 = IRQ_Context();
      if (iVar2 == 0) {
        iVar2 = FUN_00441c44(*(undefined4 *)(param_1 + 4),param_2);
        if ((iVar2 == 1) && ((*(uint *)(param_1 + 0x20) & uVar1) == uVar1)) {
          FUN_004420d0();
          iVar4 = AllocBlock(param_1);
          if (iVar4 == 0) {
            iVar4 = CreateBlock(param_1);
          }
          FUN_004420e8();
        }
      }
      else if (((param_2 == 0) &&
               (iVar2 = FUN_00441da6(*(undefined4 *)(param_1 + 4),0,0), iVar2 == 1)) &&
              ((*(uint *)(param_1 + 0x20) & uVar1) == uVar1)) {
        uVar3 = ulSetInterruptMask();
        iVar4 = AllocBlock(param_1);
        if (iVar4 == 0) {
          iVar4 = CreateBlock(param_1);
        }
        vClearInterruptMask(uVar3);
      }
    }
  }
  return CONCAT44(param_4,iVar4);
}

