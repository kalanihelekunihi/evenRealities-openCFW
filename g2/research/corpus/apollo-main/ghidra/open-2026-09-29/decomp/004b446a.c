
undefined8
FUN_004b446a(byte param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5,
            undefined4 param_6,char param_7)

{
  char cVar1;
  int iVar2;
  int iVar3;
  byte bVar4;
  
  iVar2 = DAT_004b46f4;
  cVar1 = *(char *)(DAT_004b46f4 + 0x5d);
  if (param_7 == '\x02') {
    iVar3 = FUN_0047a600();
    if (iVar3 == 0) {
      FUN_004b467c(1);
      *(undefined1 *)(iVar2 + 0x5d) = 1;
    }
    else {
      FUN_004b467c(0);
      *(undefined1 *)(iVar2 + 0x5d) = 0;
    }
  }
  else {
    FUN_004b467c(1);
    *(char *)(iVar2 + 0x5d) = param_7;
  }
  if (cVar1 != *(char *)(iVar2 + 0x5d)) {
    for (bVar4 = 0; bVar4 < param_1; bVar4 = bVar4 + 1) {
      FUN_004b33d2(*(undefined1 *)(param_2 + (uint)bVar4),*(undefined1 *)(iVar2 + 0x5d));
    }
  }
  FUN_004b42f0(param_1,param_2,param_3,param_4);
  return CONCAT44(1,param_5);
}

