
undefined1 FUN_0044ffe6(int param_1,int param_2,byte param_3)

{
  byte bVar1;
  uint uVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined1 uVar5;
  uint uVar6;
  int *piVar7;
  undefined1 auStack_38 [20];
  
  if (param_1 == 0) {
    uVar5 = 1;
  }
  else {
    if (-1 < (int)((uint)*(byte *)(param_2 + 0x18) << 0x1f)) {
      FUN_00439c04(auStack_38,param_1,0x14);
      bVar1 = *(byte *)(param_1 + 0x14);
      *(byte *)(param_1 + 0x14) = *(byte *)(param_1 + 0x14) | 1;
      uVar5 = 1;
      uVar2 = FUN_00450388(param_1);
      uVar6 = 0;
      do {
        if ((uVar2 <= uVar6) || ((int)((uint)*(byte *)(param_2 + 0x18) << 0x1f) < 0))
        goto LAB_004500b0;
        puVar3 = (undefined4 *)FUN_00450390(param_1,uVar6);
        piVar7 = (int *)*puVar3;
        if (((*piVar7 != 0) &&
            ((iVar4 = FUN_0045037e(piVar7), iVar4 == 0 &&
             (((uint)piVar7[2] >> 0xf & 1) == (uint)param_3)))) &&
           (((piVar7[2] & 0xffff7fffU) == 0 || ((piVar7[2] & 0xffff7fffU) == *(uint *)(param_2 + 8))
            ))) {
          *(int *)(param_2 + 0xc) = piVar7[1];
          (*(code *)*piVar7)(param_2);
          if ((*(byte *)(param_2 + 0x18) & 3) >> 1 != 0) goto LAB_004500b0;
          if ((int)((uint)*(byte *)(param_2 + 0x18) << 0x1f) < 0) {
            uVar5 = 0;
LAB_004500b0:
            if ((bVar1 & 1) != 0) {
              return uVar5;
            }
            if ((int)((uint)*(byte *)(param_2 + 0x18) << 0x1f) < 0) {
              FUN_004502e0(auStack_38);
              return uVar5;
            }
            *(byte *)(param_1 + 0x14) = *(byte *)(param_1 + 0x14) & 0xfe;
            FUN_00450346(param_1);
            return uVar5;
          }
        }
        uVar6 = uVar6 + 1;
      } while( true );
    }
    uVar5 = 0;
  }
  return uVar5;
}

