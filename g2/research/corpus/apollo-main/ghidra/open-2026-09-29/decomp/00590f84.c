
/* WARNING: Instruction at (ram,0x00590ff2) overlaps instruction at (ram,0x00590ff0)
    */

undefined8 FUN_00590f84(byte *param_1,short *param_2,int param_3)

{
  short sVar1;
  byte *pbVar2;
  short *psVar3;
  short *psVar4;
  uint uVar5;
  byte *pbVar6;
  uint in_fpscr;
  undefined4 uVar7;
  
  uVar5 = *(int *)(DAT_005915b8 + (uint)param_1[2] * 4) * (*param_1 + 1);
  if (0 < (int)uVar5) {
    pbVar6 = param_1 + *(int *)(param_1 + 0x4a0) * 2 + 0x4ac;
    pbVar2 = param_1 + *(int *)(param_1 + 0x4a4) * 4 + 0x4ac;
    if ((uVar5 & 3) != 0) {
      do {
        *(short *)pbVar6 = *param_2;
        sVar1 = *param_2;
        param_2 = param_2 + param_3;
        uVar7 = VectorSignedToFloat((int)sVar1,(byte)(in_fpscr >> 0x16) & 3);
        *(undefined4 *)pbVar2 = uVar7;
        pbVar2 = pbVar2 + 4;
        loopEnd();
        pbVar6 = pbVar6 + 2;
      } while( true );
    }
    if (uVar5 >> 2 != 0) {
      do {
        *(short *)pbVar6 = *param_2;
        psVar3 = param_2 + param_3;
        uVar7 = VectorSignedToFloat((int)*param_2,(byte)(in_fpscr >> 0x16) & 3);
        *(undefined4 *)pbVar2 = uVar7;
        *(short *)(pbVar6 + 2) = *psVar3;
        psVar4 = psVar3 + param_3;
        uVar7 = VectorSignedToFloat((int)*psVar3,(byte)(in_fpscr >> 0x16) & 3);
        *(undefined4 *)(pbVar2 + 4) = uVar7;
        *(short *)(pbVar6 + 4) = *psVar4;
        psVar3 = psVar4 + param_3;
        uVar7 = VectorSignedToFloat((int)*psVar4,(byte)(in_fpscr >> 0x16) & 3);
        *(undefined4 *)(pbVar2 + 8) = uVar7;
        *(short *)(pbVar6 + 6) = *psVar3;
        param_2 = psVar3 + param_3;
        uVar7 = VectorSignedToFloat((int)*psVar3,(byte)(in_fpscr >> 0x16) & 3);
        *(undefined4 *)(pbVar2 + 0xc) = uVar7;
        pbVar2 = pbVar2 + 0x10;
        loopEnd();
        pbVar6 = pbRam00590ffc;
      } while( true );
    }
    param_1 = *(byte **)pbVar2;
    param_2 = *(short **)(pbVar2 + 4);
  }
  return CONCAT44(param_2,param_1);
}

