
undefined8 FUN_004b8390(char param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  uVar1 = DAT_004b87ec;
  if ((((param_1 != '\x01') && (uVar1 = DAT_004b87f0, param_1 != '\x02')) &&
      (uVar1 = DAT_004b87f4, param_1 != '\x03')) && (uVar1 = DAT_004b87f8, param_1 != '\x04')) {
    if (param_1 == '\x05') {
      FUN_004b46ce();
      uVar1 = DAT_004b87fc;
    }
    else {
      uVar1 = DAT_004b8800;
      if ((((param_1 != '\x06') && (uVar1 = DAT_004b8804, param_1 != '\a')) &&
          ((uVar1 = DAT_004b8808, param_1 != '\b' &&
           ((uVar1 = DAT_004b880c, param_1 != '\t' && (uVar1 = DAT_004b8810, param_1 != '\n'))))))
         && ((uVar1 = DAT_004b8814, param_1 != '\v' &&
             ((((uVar1 = DAT_004b8818, param_1 != '\f' && (uVar1 = DAT_004b881c, param_1 != '\r'))
               && (uVar1 = DAT_004b8820, param_1 != '\x0e')) &&
              (uVar1 = DAT_004b8824, param_1 != -0x1f)))))) {
        uVar1 = DAT_004b8828;
      }
    }
  }
  return CONCAT44(unaff_r7,uVar1);
}

