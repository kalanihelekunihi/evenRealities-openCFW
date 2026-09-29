
undefined8 FUN_0047add4(short param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  char cVar4;
  
  cVar4 = '\n';
  iVar3 = DAT_0047ae64;
  do {
    if (cVar4 == '\0') {
      iVar3 = 0;
LAB_0047ae24:
      return CONCAT44(param_4,iVar3);
    }
    if (((*(char *)(iVar3 + 0x2f) != '\0') && (*(short *)(iVar3 + 0x4c) == param_1)) &&
       (iVar2 = FUN_004751c8(iVar3 + 0x44,param_2,8), piVar1 = DAT_0047ae50, iVar2 == 0)) {
      *DAT_0047ae50 = *DAT_0047ae50 + 1;
      *(int *)(iVar3 + 0xc4) = *piVar1;
      goto LAB_0047ae24;
    }
    cVar4 = cVar4 + -1;
    iVar3 = iVar3 + 200;
  } while( true );
}

