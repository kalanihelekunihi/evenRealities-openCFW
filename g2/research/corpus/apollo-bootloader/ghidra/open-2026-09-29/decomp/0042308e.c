
undefined8
earliest_complete_opaque_body(uint *param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  undefined1 uVar3;
  int iVar4;
  uint *puVar5;
  int iVar6;
  uint uVar7;
  
  iVar2 = DAT_00423440;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004233e0)) {
    iVar4 = 2;
  }
  else {
    uVar7 = param_1[10];
    *(undefined4 *)(DAT_00423440 + uVar7 * 0x1000 + 0x30) = 0;
    puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
    *puVar5 = *puVar5 | 8;
    if (((byte)param_2[3] < 2) && (((char)param_2[3] != '\x01' || ((*DAT_00423438 & 0xff) != 0x21)))
       ) {
      if ((char)param_2[3] == '\0') {
        uVar3 = 4;
      }
      else {
        uVar3 = 6;
      }
      *(undefined1 *)(param_1 + 0x46) = uVar3;
      if (*param_2 < DAT_00423434) {
        if (0x21 < (*DAT_00423438 & 0xff)) {
          *DAT_0042343c = *DAT_0042343c & ~(0x400000 << (uVar7 & 0xff));
        }
        if ((char)param_1[0x46] == '\x06') {
          iVar4 = 6;
        }
        else {
          iVar4 = 1;
        }
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
        *puVar5 = *puVar5 & 0xffffff8f | iVar4 << 4;
      }
      else {
        if (0x21 < (*DAT_00423438 & 0xff)) {
          *DAT_0042343c = *DAT_0042343c | 0x400000 << (uVar7 & 0xff);
        }
        if ((char)param_1[0x46] == '\x06') {
          iVar4 = 6;
        }
        else {
          iVar4 = 5;
        }
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
        *puVar5 = *puVar5 & 0xffffff8f | iVar4 << 4;
      }
      clock_request((char)param_1[0x46],uVar7 + 0xb & 0xff);
      puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
      *puVar5 = *puVar5 & 0xfffffffe;
      puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
      *puVar5 = *puVar5 & 0xfffffdff;
      puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
      *puVar5 = *puVar5 & 0xfffffeff;
      iVar4 = FUN_00422e28(uVar7,*param_2,param_1 + 0xc);
      if (iVar4 == 0) {
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
        *puVar5 = *puVar5 & 0xffffbfff;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
        *puVar5 = *puVar5 & 0xffff7fff;
        *(uint *)(iVar2 + uVar7 * 0x1000 + 0x30) =
             *(uint *)(iVar2 + uVar7 * 0x1000 + 0x30) | (uint)(ushort)param_2[2];
        iVar6 = 0;
        iVar4 = 0;
        bVar1 = *(byte *)((int)param_2 + 5);
        if (bVar1 == 0) {
          iVar6 = 1;
          iVar4 = 0;
        }
        else if (bVar1 == 2) {
          iVar6 = 0;
          iVar4 = 0;
        }
        else if (bVar1 < 2) {
          iVar6 = 1;
          iVar4 = 1;
        }
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x2c);
        *puVar5 = *puVar5 & 0xfffffffe;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x2c);
        *puVar5 = *puVar5 & 0xfffffffd | iVar6 << 1;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x2c);
        *puVar5 = *puVar5 & 0xfffffffb | iVar4 << 2;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x2c);
        *puVar5 = *puVar5 & 0xfffffff7 | (*(byte *)((int)param_2 + 6) & 1) << 3;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x2c);
        *puVar5 = *puVar5 | 0x10;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x2c);
        *puVar5 = *puVar5 & 0xffffff9f | ((byte)param_2[1] & 3) << 5;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x2c);
        *puVar5 = *puVar5 & 0xffffff7f;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x34);
        *puVar5 = *(byte *)((int)param_2 + 10) & 7 | *puVar5 & 0xfffffff8;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x34);
        *puVar5 = *puVar5 & 0xffffffc7 | (*(byte *)((int)param_2 + 0xb) & 7) << 3;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
        *puVar5 = *puVar5 | 1;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
        *puVar5 = *puVar5 | 0x200;
        puVar5 = (uint *)(iVar2 + uVar7 * 0x1000 + 0x30);
        *puVar5 = *puVar5 | 0x100;
        iVar4 = 0;
      }
    }
    else {
      iVar4 = 6;
    }
  }
  return CONCAT44(param_4,iVar4);
}

