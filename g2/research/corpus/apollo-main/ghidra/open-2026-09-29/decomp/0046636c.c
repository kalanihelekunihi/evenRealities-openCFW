
undefined8 FUN_0046636c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = DAT_004667ec;
  if (((((*(short *)(param_1 + 0x14) == *(short *)(DAT_004667ec + 0x12)) &&
        (*(char *)(param_1 + 3) == *(char *)(DAT_004667ec + 1))) &&
       (*(char *)(param_1 + 4) == *(char *)(DAT_004667ec + 2))) &&
      ((*(char *)(param_1 + 5) == *(char *)(DAT_004667ec + 3) &&
       (*(char *)(param_1 + 6) == *(char *)(DAT_004667ec + 4))))) &&
     (*(char *)(param_1 + 0xd) == *(char *)(DAT_004667ec + 0xb))) {
    iVar3 = FUN_004751c8(param_1 + 7,DAT_004667ec + 5,3);
    if (iVar3 == 0) {
      iVar3 = FUN_004751c8(param_1 + 10,iVar1 + 8,3);
      if (iVar3 == 0) {
        iVar3 = FUN_004751c8(param_1 + 0xe,iVar1 + 0xc,6);
        if (iVar3 == 0) {
          if ((*(short *)(param_1 + 0x20) == *(short *)(iVar1 + 0x1c)) &&
             (*(int *)(param_1 + 0x1c) == *(int *)(iVar1 + 0x18))) {
            if ((*(short *)(param_1 + 0x2c) == *(short *)(iVar1 + 0x28)) &&
               (*(int *)(param_1 + 0x28) == *(int *)(iVar1 + 0x24))) {
              uVar2 = 1;
            }
            else {
              uVar2 = 0;
            }
          }
          else {
            uVar2 = 0;
          }
        }
        else {
          uVar2 = 0;
        }
      }
      else {
        uVar2 = 0;
      }
    }
    else {
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(param_4,uVar2);
}

