
undefined8 FUN_004d4b32(uint param_1,byte param_2,uint param_3,uint param_4)

{
  char cVar1;
  int iVar2;
  
  if ((uint)param_2 == (param_4 & 0xff)) {
    if (param_2 == 1) {
      iVar2 = FUN_004547be(param_1,param_3);
      if (iVar2 != 0) {
        if (iVar2 < 1) {
          cVar1 = -1;
        }
        else {
          cVar1 = '\x01';
        }
        iVar2 = (int)cVar1;
        goto LAB_004d4b92;
      }
    }
    else if ((param_2 == 0) && (param_1 != param_3)) {
      if (param_3 < param_1) {
        cVar1 = '\x01';
      }
      else {
        cVar1 = -1;
      }
      iVar2 = (int)cVar1;
      goto LAB_004d4b92;
    }
    iVar2 = 0;
  }
  else {
    if ((param_4 & 0xff) < (uint)param_2) {
      cVar1 = '\x01';
    }
    else {
      cVar1 = -1;
    }
    iVar2 = (int)cVar1;
  }
LAB_004d4b92:
  return CONCAT44(param_4,iVar2);
}

