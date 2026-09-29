
undefined4 gx8002_audio_record_callback(uint param_1,int param_2)

{
  uint *puVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  int iVar12;
  
  piVar2 = piRam1002630c;
  if ((param_1 & 4) != 0) {
    iVar3 = func_0x10207404(param_2 + 8);
    *(byte *)(piVar2 + 4) = *(byte *)(piVar2 + 4) & 0xf0 | (byte)iVar3 & 0xf;
    iVar4 = func_0x10206e9c();
    uVar10 = *(uint *)(param_2 + 8) / (uint)(*(int *)(iVar4 + 0x24) * *(int *)(iVar4 + 0x6c) * 2);
    iVar4 = func_0x10206f74();
    iVar5 = func_0x10206f50();
    puVar1 = puRam10026310;
    if ((*(byte *)(piVar2 + 4) & 0xf0) != 0) {
      piVar2[1] = uVar10 + 2;
      *piVar2 = uVar10 + 2;
      piVar2[2] = uVar10;
      *(undefined1 *)(piVar2 + 4) = 1;
      piVar2[3] = 1;
      puVar1 = puRam10026310;
    }
    while (uVar11 = piVar2[1], uVar10 != uVar11 - (iVar4 / iVar5) * (uVar11 / (uint)(iVar4 / iVar5))
          ) {
      uVar6 = func_0x10206f84();
      if (uVar6 < uVar11) {
        iVar9 = *piVar2;
        iVar12 = piVar2[1];
        iVar7 = func_0x10206f84();
        iVar8 = func_0x10206f80();
        if ((uint)(iVar7 - iVar8) <= (uint)(iVar12 - iVar9)) {
          return 0;
        }
      }
      if (iVar3 == 0) {
        uVar11 = piVar2[1];
        iVar7 = func_0x10206f74();
        iVar8 = func_0x10206f50();
        if (uVar11 <= (uint)(iVar7 / iVar8)) goto LAB_100262f2;
        uVar11 = puVar1[2];
        puVar1[2] = uVar11 + 1;
        piVar2[3] = (uint)((int)(uVar11 + 1) < 0x19);
      }
      else {
LAB_100262f2:
        piVar2[3] = 1;
        puVar1[2] = 0;
      }
      (*(code *)(*puVar1 & 0xfffffffe))(piVar2[1],param_2 + 8);
      piVar2[1] = piVar2[1] + 1;
    }
  }
  return 0;
}

