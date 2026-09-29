
undefined8 FUN_004b47cc(uint param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = 3;
  do {
    if ((int)uVar2 < 0) {
      FUN_004733ee(DAT_004b4d48,param_1);
      uVar1 = 0;
LAB_004b4808:
      return CONCAT44(param_4,uVar1);
    }
    if ((param_1 >> ((uVar2 & 0x1f) << 3) & 0xff) < (param_2 >> ((uVar2 & 0x1f) << 3) & 0xff)) {
      FUN_004733ee(DAT_004b4d44,param_1);
      uVar1 = 1;
      goto LAB_004b4808;
    }
    uVar2 = uVar2 - 1;
  } while( true );
}

