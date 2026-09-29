
void FUN_004736f4(int param_1,undefined4 param_2,undefined4 param_3)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_20 [16];
  
  FUN_00439c04(auStack_20,param_2,0x10);
  iVar2 = FUN_0044fb4e(param_1);
  iVar3 = FUN_0044fb9a(param_1);
  FUN_00450bb2(auStack_20,-iVar2,-iVar3);
  FUN_0048abb8(*DAT_004738fc,0);
  cVar1 = FUN_0044fc42(param_1);
  if (cVar1 == '\0') {
    *(undefined4 *)(param_1 + 0x30) = 0;
  }
  else {
    FUN_0047381e();
    FUN_0047366c(0,param_3,1);
    FUN_0047386a();
    *(undefined4 *)(param_1 + 0x30) = 0;
    if (cVar1 != '\0') {
      FUN_0047381e();
      FUN_00474066(0,0,0,0,0x240,0x120);
    }
  }
  return;
}

