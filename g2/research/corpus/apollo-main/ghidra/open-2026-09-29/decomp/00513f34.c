
int FUN_00513f34(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int in_r3;
  bool bVar4;
  int local_10;
  
  local_10 = in_r3;
  iVar2 = FUN_0051403c(0x148);
  do {
    FUN_00514046(0xf8,0);
    FUN_00513eee(0x1c);
    iVar3 = FUN_0051403c(0x148);
    piVar1 = DAT_0051424c;
    bVar4 = iVar3 != iVar2;
    iVar2 = iVar3;
  } while (bVar4);
  *DAT_0051424c = iVar3;
  FUN_00441a42(*DAT_00514250,&local_10);
  if (local_10 != 0) {
    *DAT_00514254 = 0x10000000;
  }
  if (*DAT_00514258 != 0) {
    (*(code *)*DAT_00514258)(*piVar1);
  }
  return local_10;
}

