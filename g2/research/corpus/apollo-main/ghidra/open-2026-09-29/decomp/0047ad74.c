
undefined8 FUN_0047ad74(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  char cVar5;
  
  iVar4 = DAT_0047ae64;
  cVar2 = DmHostAddrType(param_1);
  cVar5 = '\n';
  do {
    if (cVar5 == '\0') {
      iVar4 = 0;
LAB_0047adc4:
      return CONCAT44(param_4,iVar4);
    }
    if (((*(char *)(iVar4 + 0x2f) != '\0') && (*(char *)(iVar4 + 6) == cVar2)) &&
       (iVar3 = FUN_004d294a(iVar4,param_2), piVar1 = DAT_0047ae50, iVar3 != 0)) {
      *DAT_0047ae50 = *DAT_0047ae50 + 1;
      *(int *)(iVar4 + 0xc4) = *piVar1;
      goto LAB_0047adc4;
    }
    cVar5 = cVar5 + -1;
    iVar4 = iVar4 + 200;
  } while( true );
}

