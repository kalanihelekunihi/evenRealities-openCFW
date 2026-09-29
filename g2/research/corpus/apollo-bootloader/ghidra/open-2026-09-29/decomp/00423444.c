
undefined8 FUN_00423444(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0;
  iVar1 = FUN_004234d8(param_1,param_2);
  if (iVar1 == 0) {
    do {
      if (*(char *)(param_1 + 0x119) == '\0') {
        iVar1 = 0;
        goto LAB_0042348c;
      }
      FUN_00423524(param_1);
      delay_us(1000);
    } while ((*(int *)(param_2 + 0xc) == -1) ||
            (iVar2 = iVar2 + 1, iVar2 != *(int *)(param_2 + 0xc)));
    *(undefined1 *)(param_1 + 0x119) = 0;
    iVar1 = 4;
  }
LAB_0042348c:
  return CONCAT44(param_4,iVar1);
}

