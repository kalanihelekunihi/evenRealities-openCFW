# SPDX-License-Identifier: MIT
"""Expected audio board state derived from SDK fields and recovered configuration."""
import struct
BOARD=0x20026d00


def expected(source,channel,buffer,size,frames,memory,mutation=None):
    board=bytearray(memory[BOARD+i] for i in range(240));events=[]
    def put(offset,value):struct.pack_into('<I',board,offset,value&0xffffffff)
    def words(offset,count):return struct.unpack_from('<'+'I'*count,board,offset)
    def call(target,args=()):
        events.append((target,args,bytes(board)))
        if mutation:mutation(target,board)
    call(0x105d8,(channel,));call(0x105b0,(channel,));call(0xc590)
    device=(buffer&0x0fffffff)//8*8
    if channel in (1,2):
        track=(board[5 if channel==1 else 33]>>3)&1
        single=bool(source & (9 if channel==1 else 1)) or not track
        extent=(size if single else size//2)//128*128
        offset=124 if channel==1 else 148
        if channel==2:
            call(0x104e8)
            signed=frames if frames<0x80000000 else frames-0x100000000
            frame_count=(abs(signed)//64*64)*(-1 if signed<0 else 1)
        else:frame_count=1024 if source&8 else 128
        put(offset,device);put(offset+8,extent)
        if channel==1 and source&8:
            put(220,device);put(224,size);put(228,size//8)
            call(0xdab8,(1,1));call(0xd6b8,(1,)+words(220,5))
        else:
            put(offset+4,device+extent if track else 0);put(offset+16,0)
        put(offset+12,frame_count)
        call(0xd534,(channel,)+words(offset,6))
    elif channel==4:
        put(172,device);put(176,size);put(180,1)
        call(0xdab8,(1,1));call(0xd60c,words(172,5))
    elif channel==8:
        call(0xd7b4,words(192,7));call(0xd8cc,(0,))
    return events,bytes(board)
