#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compose independently modeled transfers into one message transaction stream."""
from dataclasses import dataclass,replace
from model_gx8002_backup_spi_transfer_alignment import TRANSFER,STATE,MESSAGE,expected as alignment
from model_gx8002_backup_spi_transfer_tx import Case as TXCase,expected as transmit
from model_gx8002_backup_spi_transfer_rx import Case as RXCase,expected as receive

@dataclass(frozen=True)
class Case:
    transfers: tuple
    shared_buffers: bool = False


def expected(case):
    if not case.transfers: raise ValueError('Use lifecycle model for an empty message')
    regions=[]
    for transfer in case.transfers:
        region=(transfer.buffer,transfer.buffer+transfer.length)
        if not case.shared_buffers and transfer.length and any(region[0]<end and start<region[1] for start,end in regions):
            raise ValueError('Aliased buffers require a shared-memory model')
        if transfer.length: regions.append(region)
    memory={}
    if case.shared_buffers:
        for transfer in case.transfers:
            if not 0x20030000<=transfer.buffer<=transfer.buffer+transfer.length<=0x20040000:
                raise ValueError('Shared buffers must be separate from modeled metadata')
            if isinstance(transfer,TXCase):
                for offset,value in enumerate(transfer.data[:transfer.length]):
                    address=transfer.buffer+offset
                    if address in memory and memory[address]!=value:
                        raise ValueError('Conflicting initial TX buffer contents')
                    memory[address]=value
    combined=[]
    for index,transfer in enumerate(case.transfers):
        if isinstance(transfer,TXCase):
            if case.shared_buffers:
                transfer=replace(transfer,data=bytes(memory[transfer.buffer+i] for i in range(transfer.length)))
            trace,result=transmit(transfer)
        elif isinstance(transfer,RXCase): trace,result=receive(transfer)
        else: trace,result=alignment(transfer)
        if case.shared_buffers and isinstance(transfer,RXCase):
            for kind,address,value in (item for item in trace if item[0] in ('write','write8','write16')):
                if transfer.buffer<=address<transfer.buffer+transfer.length:
                    size={'write':4,'write8':1,'write16':2}[kind]
                    for offset in range(size): memory[address+offset]=(value>>(offset*8))&255
        base=TRANSFER+index*64
        next_node=TRANSFER+(index+1)*64+24 if index+1<len(case.transfers) else MESSAGE
        mapped=[]
        for item in trace:
            kind,*args=item
            if kind.startswith(('read','write')):
                address,value=args
                original=address
                if TRANSFER<=address<TRANSFER+32: address+=index*64
                if kind=='write' and original==STATE+20 and value==TRANSFER: value=base
                if kind=='read' and original==MESSAGE and value==TRANSFER+24: value=base+24
                if kind=='read' and original==TRANSFER+24 and value==MESSAGE: value=next_node
                mapped.append((kind,address,value))
            else: mapped.append(item)
        # Each isolated proof has the same message prologue and shutdown.
        # Keep them once; preserve each transfer's next-node and state rereads.
        if mapped[9][0:2]!=('read',MESSAGE): raise ValueError('Transfer prologue changed')
        if index==0: combined.extend(mapped[:10])
        combined.extend(mapped[10:-4])
        if result or index+1==len(case.transfers):
            combined.extend(mapped[-4:])
            return combined,result
    raise AssertionError('Missing message completion')
