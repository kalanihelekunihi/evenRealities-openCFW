
undefined8 smpiActProcSecurityReq(int param_1,int param_2)

{
  undefined1 uVar1;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  ushort uStack_10;
  undefined1 uStack_e;
  undefined1 uStack_d;
  
  uStack_d = (undefined1)((uint)unaff_r5 >> 0x18);
  *(undefined1 *)(param_1 + 0x3b) = 1;
  uVar1 = *(undefined1 *)(*(int *)(param_2 + 4) + 9);
  uStack_10 = (ushort)*(byte *)(param_1 + 0x3d);
  uStack_e = 0x32;
  DmSmpCbackExec(&uStack_10);
  return CONCAT44(CONCAT31((int3)((uint)unaff_r6 >> 8),uVar1),
                  CONCAT13(uStack_d,CONCAT12(uStack_e,uStack_10)));
}

