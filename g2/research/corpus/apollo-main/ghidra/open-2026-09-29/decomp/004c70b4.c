
undefined8 FUN_004c70b4(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  
  uVar2 = DAT_004c732c;
  puVar1 = (undefined4 *)FUN_00482cd8(DAT_004c732c);
  do {
    if (puVar1 == (undefined4 *)0x0) {
      uVar2 = 0;
LAB_004c70e2:
      return CONCAT44(param_4,uVar2);
    }
    if (*(char *)*puVar1 == param_1) {
      uVar2 = *puVar1;
      goto LAB_004c70e2;
    }
    puVar1 = (undefined4 *)FUN_00482cf0(uVar2,puVar1);
  } while( true );
}

