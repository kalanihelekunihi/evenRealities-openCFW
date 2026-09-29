
void FUN_0047f56e(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = DAT_0047ffbc;
  iVar2 = FUN_004807fc(100,DAT_0047ffbc,0x100,0x100);
  if ((iVar2 != 0) && (iVar2 = FUN_004807fc(100,DAT_0047ffc0,1,1), iVar2 == 0)) {
    *DAT_004800f4 = *DAT_004800f4 | 1;
    FUN_004807fc(100,uVar1,0x100,0x100);
  }
  return;
}

