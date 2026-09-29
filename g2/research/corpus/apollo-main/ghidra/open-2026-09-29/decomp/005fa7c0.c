
void FUN_005fa7c0(int param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  uint in_fpscr;
  float fVar2;
  float fVar3;
  float fVar4;
  int iVar5;
  
  iVar1 = *(int *)(*DAT_005fa84c + param_4 * 0x18 + 0x3c);
  FUN_004b1516(0,0,iVar1,1);
  FUN_00513924(1,param_4,0xffffffff);
  fVar4 = (float)VectorUnsignedToFloat(param_1,(byte)(in_fpscr >> 0x16) & 3);
  fVar3 = (float)VectorUnsignedToFloat(param_2 + param_1,(byte)(in_fpscr >> 0x16) & 3);
  fVar2 = (float)VectorUnsignedToFloat(iVar1,(byte)(in_fpscr >> 0x16) & 3);
  fVar2 = (fVar4 / fVar3) * fVar2;
  iVar5 = (uint)(0.0 < fVar2) * (int)fVar2;
  FUN_00522a16(param_3);
  FUN_00522ae0(0,0,iVar5,1);
  FUN_00522a16(0);
  FUN_00522ae0(iVar5,0,iVar1 - iVar5,1);
  FUN_004b1548();
  return;
}

