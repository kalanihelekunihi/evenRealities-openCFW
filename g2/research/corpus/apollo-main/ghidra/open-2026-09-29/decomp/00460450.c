
undefined8
FUN_00460450(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 *param_4,
            undefined1 *param_5)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  iVar1 = DAT_0046102c;
  uVar3 = 0;
  do {
    if (7 < uVar3) {
      uVar2 = 0xffffffff;
LAB_004604be:
      return CONCAT44(param_4,uVar2);
    }
    if (*(int *)(uVar3 * 0x34 + DAT_0046102c + 0x30) == param_1) {
      *param_2 = *(undefined4 *)(DAT_0046102c + uVar3 * 0x34);
      uVar2 = FUN_0044a43c(uVar3 * 0x34 + iVar1 + 4);
      FUN_00439be4(param_3,uVar3 * 0x34 + iVar1 + 4,uVar2);
      *param_4 = *(undefined4 *)(uVar3 * 0x34 + iVar1 + 0x24);
      *param_5 = *(undefined1 *)(iVar1 + uVar3 * 0x34 + 0x28);
      uVar2 = 0;
      goto LAB_004604be;
    }
    uVar3 = uVar3 + 1;
  } while( true );
}

