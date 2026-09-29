
/* WARNING: Removing unreachable block (ram,0x08000292) */
/* WARNING: Removing unreachable block (ram,0x0800029a) */
/* WARNING: Removing unreachable block (ram,0x080002a4) */
/* WARNING: Removing unreachable block (ram,0x08000350) */
/* WARNING: Removing unreachable block (ram,0x08000372) */
/* WARNING: Removing unreachable block (ram,0x0800039a) */
/* WARNING: Removing unreachable block (ram,0x08000384) */
/* WARNING: Removing unreachable block (ram,0x080003a4) */
/* WARNING: Removing unreachable block (ram,0x080003d8) */
/* WARNING: Removing unreachable block (ram,0x080003c0) */
/* WARNING: Removing unreachable block (ram,0x080003e2) */
/* WARNING: Removing unreachable block (ram,0x08000402) */
/* WARNING: Removing unreachable block (ram,0x080003e8) */
/* WARNING: Removing unreachable block (ram,0x0800040e) */
/* WARNING: Removing unreachable block (ram,0x080003f4) */
/* WARNING: Removing unreachable block (ram,0x080003f8) */
/* WARNING: Removing unreachable block (ram,0x08000400) */
/* WARNING: Removing unreachable block (ram,0x08000406) */
/* WARNING: Removing unreachable block (ram,0x080003ce) */
/* WARNING: Removing unreachable block (ram,0x08000390) */
/* WARNING: Removing unreachable block (ram,0x0800035e) */

undefined8 case_boot_initialize(void)

{
  byte bVar1;
  byte *pbVar2;
  byte *pbVar3;
  byte *pbVar4;
  uint uVar5;
  uint uVar6;
  byte *pbVar7;
  bool bVar8;
  bool bVar9;
  undefined8 uVar10;
  
  pbVar3 = pbRam08000290;
  pbVar7 = pbRam0800028c;
  while( true ) {
    bVar9 = pbVar3 <= pbVar7;
    bVar8 = pbVar7 == pbVar3;
    if (bVar9) break;
    (**(code **)(pbVar7 + 0xc))
              (*(undefined4 *)pbVar7,*(undefined4 *)(pbVar7 + 4),*(undefined4 *)(pbVar7 + 8));
    pbVar7 = pbVar7 + 0x10;
  }
  uVar10 = thunk_FUN_0800a598();
  if (!bVar9 || bVar8) {
    while( true ) {
      pbVar4 = (byte *)((ulonglong)uVar10 >> 0x20);
      pbVar3 = (byte *)uVar10;
      if (pbVar7 <= pbVar4) break;
      bVar1 = *pbVar3;
      pbVar2 = pbVar3 + 1;
      uVar6 = bVar1 & 0xf;
      if ((bVar1 & 0xf) == 0) {
        uVar6 = (uint)*pbVar2;
        pbVar2 = pbVar3 + 2;
      }
      uVar5 = (uint)(bVar1 >> 4);
      if (uVar5 == 0) {
        uVar5 = (uint)*pbVar2;
        pbVar2 = pbVar2 + 1;
      }
      while (uVar6 = uVar6 - 1, uVar6 != 0) {
        *pbVar4 = *pbVar2;
        pbVar2 = pbVar2 + 1;
        pbVar4 = pbVar4 + 1;
      }
      while( true ) {
        uVar10 = CONCAT44(pbVar4,pbVar2);
        uVar5 = uVar5 - 1;
        if (uVar5 == 0) break;
        *pbVar4 = 0;
        pbVar4 = pbVar4 + 1;
      }
    }
    return 0;
  }
  case_pulse8_extended();
  pbVar7[8] = 0x20;
  pbVar7[9] = 0;
  pbVar7[10] = 0;
  pbVar7[0xb] = 0;
  return 0;
}

