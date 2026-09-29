
undefined4 FUN_00503b92(ushort *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  iVar2 = 0;
  if (((((char)param_1[1] == '\'') || ((char)param_1[1] == '(')) || ((char)param_1[1] == '@')) &&
     (((*param_1 != 0 && (*param_1 != 0)) && (*param_1 < 4)))) {
    iVar2 = DAT_0050411c + (uint)*param_1 * 0x30 + -0x30;
  }
  cVar1 = (char)param_1[1];
  if (cVar1 == ' ') {
    *(undefined1 *)(DAT_005040bc + 0x9d) = 0xff;
    return unaff_r7;
  }
  if (cVar1 == '$') {
LAB_00503c06:
    FUN_0050366e();
  }
  else {
    if (cVar1 == '%') {
LAB_00503c0c:
      FUN_0050367c();
      return unaff_r7;
    }
    if (cVar1 != '&') {
      if (cVar1 == '\'') {
        FUN_005037c4(param_1,iVar2);
        return unaff_r7;
      }
      if (cVar1 == '(') {
        FUN_005037d0();
        return unaff_r7;
      }
      if (cVar1 == '7') {
        FUN_0050393e();
        return unaff_r7;
      }
      if (cVar1 == '@') {
        FUN_00503b24();
        return unaff_r7;
      }
      if (cVar1 == 'J') goto LAB_00503c06;
      if (cVar1 == 'K') goto LAB_00503c0c;
      if (cVar1 != 'L') {
        return unaff_r7;
      }
    }
    FUN_005037bc();
  }
  return unaff_r7;
}

