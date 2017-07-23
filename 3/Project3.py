# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 16:59:29 2017

@author: christopherhedenberg
"""
import numpy as np
from Project1 import Mips_Decoder
import copy

class ifidReg():
    def __init__(self,InstSet=0x00000000,):
        self.InstSet = InstSet
        self.PC = 0

class idexReg():
    def __init__(self,RegDest=0,Jump=0,Branch=0,MemRead=0,MemToReg=0,ALUOp=0,MemWrite=0,ALUSrc=0,RegWrite=0,Read1=0,Read2=0,Offset=0):
        self.RegDest = RegDest
        self.Jump =  Jump
        self.Branch = Branch
        self.MemRead = MemRead
        self.MemToReg = MemToReg
        self.ALUOp = ALUOp
        self.MemWrite = MemWrite
        self.ALUSrc = ALUSrc
        self.RegWrite = RegWrite
        self.Read1 = Read1
        self.Read2 = Read2
        self.Offset = Offset
        self.dest = 0
        self.srcordest = 0

class exmemReg():
    def __init__(self,MemWrite=0,MemRead=0,Branch=0,MemToReg=0,RegWrite=0):
        self.MemWrite = MemWrite
        self.Branch = Branch
        self.MemRead = MemRead
        self.MemToReg = MemToReg
        self.RegWrite = RegWrite
        self.ALUResult = 0
        self.WriteData = 0
        self.WriteRegister = 0
        self.zero = 0
        
        
class memwbReg():
    def __init__(self,MemToReg=0,RegWrite=0):
        self.MemToReg = MemToReg
        self.RegWrite = RegWrite
        self.ALUResult = 0
        self.WriteRegister = 0
        self.ReadData = 0
        
        
class Pipeline():
    def __init__(self):
        self.Regs = [0x100 + i for i in range(32)]
        self.Regs[0]=0
        self.MainMem=[(i%(0xFF+1)) for i in range(1024)]
        self.PC = 0
        self.ifidRegRd = ifidReg()
        self.ifidRegWr = ifidReg()
        self.idexRegRd = idexReg()
        self.idexRegWr = idexReg()
        self.exmemRegRd = exmemReg()
        self.exmemRegWr = exmemReg()
        self.memwbRegRd = memwbReg()
        self.memwbRegWr = memwbReg() 
        self.InstructionCache = [0xa1020000,0x810AFFFC,0x00831820,0x01263820,0x01224820,0x81180000,0x81510010,0x00624022,0x00000000,0x00000000,0x00000000,0x00000000]  
        self.InstructionCache = [0x810f0004,0x00000000,0x00000000,0x00000000,0x00000000]
        
    def IF_stage(self):
        self.ifidRegWr.InstSet = self.InstructionCache[self.PC]
        self.ifidRegWr.PC+=1
        self.PC+=1
        
    def ID_stage(self):
        decoded = Mips_Decoder(self.ifidRegRd.InstSet, self.PC)
        self.idexRegWr.RegDest = 0 if self.ifidRegRd.InstSet == 0 else (decoded.opcode==0)
        self.idexRegWr.Jump = 0
        self.idexRegWr.Branch = (decoded.opcode ==0x04 or decoded.opcode == 0x05)
        self.idexRegWr.MemRead = decoded.opcode ==0x20
        self.idexRegWr.MemToReg = decoded.opcode ==0x20
        self.idexRegWr.ALUOp = 0 if self.ifidRegRd.InstSet == 0 else ((decoded.opcode == 0)*2) | ((decoded.opcode==0x04 or decoded.opcode==0x05)*1)
        self.idexRegWr.MemWrite = decoded.opcode == 0x28
        self.idexRegWr.ALUSrc = (decoded.opcode==0x20 or decoded.opcode==0x28)*1
        self.idexRegWr.RegWrite = 0 if self.ifidRegRd.InstSet == 0 else (decoded.opcode ==0 or decoded.opcode ==0x20)*1
        self.idexRegWr.Read1 = self.Regs[decoded.src1]
        self.idexRegWr.Read2 = self.Regs[decoded.srcordest]
        self.idexRegWr.Offset  = np.short(self.ifidRegRd.InstSet & 0xFFFF)
        if (abs(self.idexRegWr.Offset >> 16)) ==1:
            self.idexRegWr.Offset = self.idexRegWr.Offset | 0xFFFF0000
        else:
            self.idexRegWr.Offset = self.idexRegWr.Offset | 0x00000000
        self.idexRegWr.srcordest = decoded.srcordest
        self.idexRegWr.dest = (self.ifidRegRd.InstSet >> (11)) & 0x1F
        
    def EX_stage(self):
        self.exmemRegWr.Branch=copy.deepcopy(self.idexRegRd.Branch)
        self.exmemRegWr.MemRead = copy.deepcopy(self.idexRegRd.MemRead)
        self.exmemRegWr.MemToReg= copy.deepcopy(self.idexRegRd.MemToReg)
        self.exmemRegWr.MemWrite= copy.deepcopy(self.idexRegRd.MemWrite)
        self.exmemRegWr.RegWrite= copy.deepcopy(self.idexRegRd.RegWrite)
        self.exmemRegWr.WriteRegister = (self.idexRegRd.RegDest*self.idexRegRd.dest) + (1-self.idexRegRd.RegDest)*self.idexRegRd.srcordest
        self.exmemRegWr.WriteData = self.idexRegRd.Read2 +0
        ALUMux = (self.idexRegRd.ALUSrc*self.idexRegRd.Offset) + (1-self.idexRegRd.ALUSrc)*self.idexRegRd.Read2
        if self.idexRegRd.ALUOp == 0:
            self.exmemRegWr.ALUResult = self.idexRegRd.Read1 + ALUMux
        elif self.idexRegRd.ALUOp == 0:
            self.exmemRegWr.ALUResult = self.idexRegRd.Read1 - ALUMux
        else:
            ALUFunc = self.idexRegRd.Offset & 0x3F
            if ALUFunc == 0b100000:
                self.exmemRegWr.ALUResult = self.idexRegRd.Read1 + ALUMux
            else: # ALUFunc == 0b100000:
                self.exmemRegWr.ALUResult = self.idexRegRd.Read1 - ALUMux
        self.exmemRegWr.zero =  self.exmemRegWr.ALUResult==0
                
        

    def MEM_stage(self):
        self.memwbRegWr.RegWrite = self.exmemRegRd.RegWrite + 0
        self.memwbRegWr.MemToReg =self.exmemRegRd.MemToReg + 0
        self.memwbRegWr.ALUResult =  self.exmemRegRd.ALUResult + 0
        self.memwbRegWr.WriteRegister = self.exmemRegRd.WriteRegister + 0
        if self.exmemRegRd.MemWrite == 1:
            self.MainMem[self.exmemRegRd.ALUResult] = self.exmemRegRd.WriteData
        elif self.exmemRegRd.MemRead == 1:
            self.memwbRegWr.ReadData = self.MainMem[self.exmemRegRd.ALUResult]
            
        
    def WB_stage(self):
        RegWriteMux = self.memwbRegRd.MemToReg*self.memwbRegRd.ReadData + (1-self.memwbRegRd.MemToReg)*self.memwbRegRd.ALUResult
        if self.memwbRegRd.RegWrite == 1:
            self.Regs[self.memwbRegRd.WriteRegister]=RegWriteMux
            

    def Print_out_everything(self, printing = True):
        Pipeline_String = "PipeLine Contents: \n"
        for i,item in enumerate(self.Regs):
            Pipeline_String += " Register $%s: %s\n" %(i,format(item,'#04x'))
        IfIdWr_String = "IF/ID Write Register Contents:\n" + self.formatIFIDOutput(self.ifidRegWr.__dict__) + "\n"
        IfIdRd_String = "IF/ID Read Register Contents:\n" + self.formatIFIDOutput(self.ifidRegRd.__dict__) + "\n"
        IdExWr_String = "ID/EX Write Register Contents: \n" + self.formatIDEXOutput(self.idexRegWr.__dict__)+"\n"
        IdExRd_String = "ID/EX Write Register Contents: \n" + self.formatIDEXOutput(self.idexRegRd.__dict__) +"\n"
        EXMemWr_String = "EX/MEM Write Register Contents: \n" + self.formatEXMEMOutput(self.exmemRegWr.__dict__) + "\n"
        EXMemRd_String = "EX/MEM Write Register Contents: \n" + self.formatEXMEMOutput(self.exmemRegRd.__dict__) + "\n"
        MemWbWr_String = "MEM/WB Write Register Contents: \n" + self.formatMEMWBOutput(self.memwbRegWr.__dict__) + "\n"
        MemWbRd_String = "MEM/WB Write Register Contents: \n" + self.formatMEMWBOutput(self.memwbRegRd.__dict__) + "\n"
        if printing == True:
            print( Pipeline_String +"\n"+ IfIdWr_String + "\n"+ IfIdRd_String + "\n" + IdExWr_String + "\n\n" + IdExRd_String + "\n\n"+ EXMemWr_String+ "\n\n"+ EXMemRd_String + "\n\n" + MemWbWr_String+ "\n\n" + MemWbRd_String)
        else:
            return Pipeline_String +"\n"+ IfIdWr_String + "\n"+ IfIdRd_String + "\n" + IdExWr_String + "\n\n" + IdExRd_String + "\n\n"+ EXMemWr_String+ "\n\n"+ EXMemRd_String + "\n\n" + MemWbWr_String+ "\n\n" + MemWbRd_String
    
    def formatIFIDOutput(self,reg):
        outstr = ""
        for i, item in enumerate(reg):
            if item=='PC':
                outstr+="%s: %s, "%(item,reg[item])
            else:
                outstr+="%s: %s, "%(item,format(reg[item],'#04x'))
        return outstr
            
    def formatIDEXOutput(self,reg):
        outstr = ""
        for i, item in enumerate(reg):
            if item=='MemWrite' or item=='MemToReg' or item=='ALUSrc' or item=='RegWrite' or item=='Jump' or item=='Branch' or item=='RegDest' or item=='MemRead':
                outstr+=",%s: %s "%(item,int(reg[item]))
            elif item=='dest' or item=='srcordest':
                outstr+=",%s: $%s "%(item,int(reg[item]))
            elif item=='ALUOp':
                outstr+="%s: %s "%(item,bin(reg[item]))
            else:
                outstr+=",%s: %s "%(item,format(reg[item],'#04x'))
        return outstr
                    
    def formatEXMEMOutput(self,reg):
        outstr = ""
        for i, item in enumerate(reg):
            if item=='MemWrite' or item=='MemToReg' or item=='RegWrite' or item=='Branch' or item=='MemRead' or item=='zero':
                outstr+=",%s: %s "%(item,int(reg[item]))
            elif item=='WriteRegister':
                outstr+=",%s: $%s "%(item,int(reg[item]))
            elif item == 'WriteData':
                outstr+="%s: %s "%(item,format(reg[item],'#04x'))
            else:
                outstr+=",%s: %s "%(item,format(reg[item],'#04x'))
        return outstr
        
    def formatMEMWBOutput(self,reg):
        outstr = ""
        for i, item in enumerate(reg):
            if item=='MemToReg' or item=='RegWrite':
                outstr+=",%s: %s "%(item,int(reg[item]))
            elif item=='WriteRegister':
                outstr+=",%s: $%s "%(item,int(reg[item]))
            elif item == 'ALUResult':
                outstr+="%s: %s "%(item,format(reg[item],'#04x'))
            else:
                outstr+=",%s: %s "%(item,format(reg[item],'#04x'))
        return outstr
        
    def Copy_write_to_read(self):
        self.ifidRegRd = copy.deepcopy(self.ifidRegWr)
        self.idexRegRd = copy.deepcopy(self.idexRegWr)
        self.exmemRegRd = copy.deepcopy(self.exmemRegWr)
        self.memwbRegRd = copy.deepcopy(self.memwbRegWr)
        


outfile = open("/Users/christopherhedenberg/Downloads/courses/Architecture/Project3Output.txt.",'w')

Processor = Pipeline()
for item in Processor.InstructionCache:
    Processor.IF_stage()
    Processor.ID_stage()
    Processor.EX_stage()
    Processor.MEM_stage()
    Processor.WB_stage()
    outfile.write(Processor.Print_out_everything(printing=False))
    Processor.Copy_write_to_read()
    
outfile.close()