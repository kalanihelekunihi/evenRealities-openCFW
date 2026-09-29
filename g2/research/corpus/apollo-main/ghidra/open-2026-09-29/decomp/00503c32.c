
undefined4 FUN_00503c32(ushort *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  iVar2 = 0;
  if (((((char)param_1[1] != '?') && ((char)param_1[1] != 'y')) && (*param_1 != 0)) &&
     ((*param_1 != 0 && (*param_1 < 4)))) {
    iVar2 = DAT_0050411c + (uint)*param_1 * 0x30 + -0x30;
  }
  cVar1 = (char)param_1[1];
  if (cVar1 == '\'') {
    if (iVar2 != 0) {
      FUN_005037ea();
    }
  }
  else if (cVar1 == '(') {
    if (iVar2 != 0) {
      FUN_00503810();
    }
  }
  else if (cVar1 == '*') {
    if (iVar2 != 0) {
      FUN_005038da();
    }
  }
  else if (cVar1 == '+') {
    if (iVar2 != 0) {
      FUN_0050390c();
    }
  }
  else if (cVar1 == ',') {
    if (iVar2 != 0) {
      FUN_0050391c();
    }
  }
  else if (cVar1 == '-') {
    FUN_004bb04a((char)*param_1);
  }
  else if (cVar1 == '/') {
    if (iVar2 != 0) {
      FUN_005038b8();
    }
  }
  else if (cVar1 == '2') {
    if (iVar2 != 0) {
      FUN_00503820();
    }
  }
  else if (cVar1 == ':') {
    if (iVar2 != 0) {
      FUN_00503880();
    }
  }
  else if (cVar1 == ';') {
    if (iVar2 != 0) {
      FUN_0050389e();
    }
  }
  else if (cVar1 == '?') {
    if (iVar2 != 0) {
      FUN_0050386c();
    }
  }
  else if (cVar1 == 'y') {
    HciDrvRadioBoot(0);
    DmDevReset();
  }
  return unaff_r7;
}

