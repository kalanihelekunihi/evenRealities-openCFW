
undefined8 FUN_00551018(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  char *pcVar6;
  char cVar7;
  short sVar8;
  int iVar9;
  char cVar10;
  short sVar11;
  ushort uVar12;
  
  pcVar6 = DAT_00551aa8;
  cVar1 = *DAT_00551aa4;
  if ('\0' < cVar1) {
    uVar12 = (short)cVar1 - 1;
    sVar8 = FUN_0055025c(*DAT_00551aa8);
    iVar9 = DAT_00551e9c;
    if (sVar8 < 0) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        param_2 = 0x534;
        param_3 = DAT_00551aac;
        FUN_0043d574(2,DAT_005514b8,DAT_0055148c,DAT_00551ab0,0x534,DAT_00551aac,(int)*pcVar6);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_00551ab4,DAT_00551ab4,(int)*pcVar6);
      }
    }
    else {
      cVar2 = (char)uVar12;
      if ((int)sVar8 < cVar2 + -1) {
        sVar11 = sVar8 + 1;
      }
      else {
        sVar11 = cVar1 + -2;
      }
      if (cVar2 < '\x03') {
        sVar11 = sVar8;
      }
      cVar7 = (char)sVar11;
      cVar10 = '\x01';
      cVar5 = (char)sVar8;
      cVar4 = cVar1 - cVar5;
      cVar3 = cVar4 + -1;
      if (cVar2 < '\x03') {
        FUN_00550d3c(uVar12 & 0xff);
        FUN_00550e2e((int)cVar7,0);
      }
      else {
        if ((cVar5 == '\0') && ('\x02' < cVar3)) {
          cVar10 = '\x01';
          cVar7 = '\x02';
        }
        else if ((cVar5 == '\x01') && ('\x01' < cVar3)) {
          cVar10 = '\x01';
          cVar7 = '\x02';
        }
        else if ((cVar5 < '\x02') || (cVar3 != '\x01')) {
          if (('\x02' < cVar5) && (cVar4 == '\x01')) {
            cVar10 = -1;
            cVar7 = cVar5 + -2;
          }
        }
        else {
          cVar10 = -1;
          cVar7 = cVar5 + -1;
        }
        if ((cVar5 != '\0') && (cVar4 != '\x01')) {
          if (cVar10 == -1) {
            FUN_0043dfa4(*(undefined4 *)(DAT_00551e9c + 0x38),1);
            FUN_0043f09a(*(undefined4 *)(iVar9 + 0x38),0,0);
            param_2 = 0;
            FUN_0043f6d6(*(undefined4 *)(iVar9 + 0x38),*(undefined4 *)(iVar9 + 0xc),4,0,0,param_3,
                         param_4);
          }
          else if (cVar10 == '\x01') {
            FUN_0043dfa4(*(undefined4 *)(DAT_00551e9c + 0x38),1);
            FUN_0043f09a(*(undefined4 *)(iVar9 + 0x38),0,0);
            param_2 = 0;
            FUN_0043f6d6(*(undefined4 *)(iVar9 + 0x38),*(undefined4 *)(iVar9 + 0xc),1,0,0,param_3,
                         param_4);
          }
        }
        FUN_00550ef4((int)cVar1,(int)cVar7,200,(int)cVar10);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

