
void FUN_0053d708(int param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  uint in_fpscr;
  float fVar4;
  float fVar5;
  undefined4 uVar6;
  int local_58;
  int local_54;
  undefined1 auStack_50 [36];
  undefined1 auStack_2c [20];
  
  iVar1 = FUN_00450bcc(auStack_2c,param_2[2],param_1 + 0x38);
  if (iVar1 != 0) {
    iVar1 = *(int *)(param_1 + 0x4c);
    puVar3 = (undefined4 *)*param_2;
    FUN_0051566c(0x501);
    local_58 = *(int *)param_2[2];
    local_54 = *(int *)(param_2[2] + 4);
    uVar2 = FUN_00529bfe(*(undefined4 *)param_2[4]);
    fVar4 = (float)VectorUnsignedToFloat(uVar2,(byte)(in_fpscr >> 0x16) & 3);
    fVar4 = (fVar4 / DAT_0053da50) / DAT_0053da50;
    FUN_00561810(auStack_50);
    FUN_005618b8(fVar4,-fVar4,auStack_50);
    uVar6 = VectorSignedToFloat(local_54 + (uint)*(ushort *)(param_2[4] + 8) +
                                (int)*(short *)(param_2[4] + 0xc),(byte)(in_fpscr >> 0x16) & 3);
    uVar2 = VectorSignedToFloat(local_58 - *(short *)(param_2[4] + 10),(byte)(in_fpscr >> 0x16) & 3)
    ;
    FUN_00561856(uVar2,uVar6,auStack_50);
    FUN_00515634(1);
    FUN_005150ea(*(undefined4 *)(iVar1 + 0x48),0);
    FUN_00439be4(&local_58,param_2 + 5,3);
    uVar2 = FUN_004b06a8(local_58,*(undefined1 *)((int)param_2 + 0x17));
    FUN_00515136(*(undefined4 *)(iVar1 + 0x48),uVar2);
    FUN_00514f60(*puVar3,auStack_50);
    FUN_005202ec(*puVar3,*(undefined4 *)(iVar1 + 0x48));
    if (0 < (int)param_2[7]) {
      FUN_00515634(0);
      fVar5 = (float)VectorSignedToFloat(param_2[7],(byte)(in_fpscr >> 0x16) & 3);
      FUN_00515640(fVar5 / fVar4);
      FUN_00439be4(&local_58,param_2 + 6,3);
      uVar2 = FUN_004b06a8(local_58,*(undefined1 *)((int)param_2 + 0x1b));
      FUN_00515136(*(undefined4 *)(iVar1 + 0x48),uVar2);
      FUN_00514f60(puVar3[1],auStack_50);
      FUN_005202ec(puVar3[1],*(undefined4 *)(iVar1 + 0x48));
    }
  }
  return;
}

