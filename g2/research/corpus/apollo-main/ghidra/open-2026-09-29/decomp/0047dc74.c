
void FUN_0047dc74(void)

{
  bool bVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = FUN_0047dce4();
  uVar4 = xTaskGetTickCount();
  puVar2 = DAT_0047e278;
  if (uVar4 < *DAT_0047e278) {
    *DAT_0047e27c = *DAT_0047e27c + 1;
  }
  *puVar2 = uVar4;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  FUN_0047cc60(uVar4,*DAT_0047e27c,1000,0);
  return;
}

