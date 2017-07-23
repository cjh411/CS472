# -*- coding: utf-8 -*-
"""
Created on Tue May 30 21:42:11 2017

@author: christopherhedenberg
"""
import numpy as np




insts= [0x032BA020, 0x8CE90014, 0x12A90003, 0x022DA822, 0xADB30021, 0x02697824, 0xAE8FFFF1,
0x018C6020, 0x02A4A825, 0x158FFFF7]

# Testing BNE FROM lecture notes 
#insts=[0x10E80008]

#TESTING LECTURE EXAMPLES
#add_inst = 0x00A63820
#sub_inst = 0x014B4822
#lw_inst = 0x8ef10004
#sw_inst = 0xafb5fffc
#beq_inst =0x12320004
#
#insts = [add_inst,sub_inst,lw_inst,sw_inst,beq_inst,0b10001110100001110000000000000100]

class Mips_Decoder():
    
    def __init__(self,Inst,addr):
        self.Inst = Inst
        self.opcode = self.getOpcode()
        self.InstFormat = self.getFormat()
        self.funcDict = {0b100000:"add",0b100100:"and",0b100101:"or",0b100010:"sub",0x2A:"slt"}
        self.opcodeDict = {0x04:"beq",0x05:"bne",0x23:"lw",0x2B:"sw",0x20:'lb',0x28:'sb'}
        self.address = addr
        if self.InstFormat == "R":
            self.func = self.getFunc()
            self.src1 = self.getSrc()
            self.srcordest = self.getSrcOrDes()
            self.dest =  self.getDes()
        else:
            self.src1 = self.getSrc()
            self.srcordest = self.getSrcOrDes()
            self.offset = self.getOffset()
            
            
    def getFormat(self):
        if self.opcode == 0:
            return "R"
        else:
            return "I"
            
    def getFunc(self):
        if self.InstFormat == "R":
            return self.Inst & 0x3F
        else:
            raise ValueError("I Format Instructions Have no Function")
        
    def getSrc(self):
        return (self.Inst >> (32-11)) & 0x1F
        
    def getSrcOrDes(self):
        return (self.Inst >> (32-16)) & 0x1F
            
    def getDes(self):
        if self.InstFormat == "R":
            return (self.Inst >> (11)) & 0x1F   
    
    def getOffset(self):
        if self.InstFormat == "R":
            raise ValueError("R Format Instructions Have no Offset")
        else:
            return np.short(self.Inst & 0xFFFF)
            
    def getOpcode(self):
        return (self.Inst >> (26)) & 0x3F  
    
    def PrintInst(self):
        string = ""
        if self.InstFormat == "R":
            string += self.funcDict[self.func] 
            string += " $%i" %self.dest
            string += " $%i" %self.src1
            string += " $%i" %self.srcordest
        elif self.opcode != 0x04 and self.opcode != 0x05 :
            string+= self.opcodeDict[self.opcode]
            string += " $%i" %self.srcordest
            string += ", %i" %self.offset
            string += " ($%i)" %self.src1
        else:
            string+= self.opcodeDict[self.opcode]
            string += " $%i" %self.src1
            string += ", $%i" %self.srcordest
            string += ", Address %s" %format(self.address + 4 + ((+self.offset)<<2),"#04x")
            
        return string
        
address=  0X9A040 
output = open('MipsHWOutput.txt','w')
output.write("CS472 MIPS Instruction Homework Answers\nChris Hedenberg\n\n")     
for item in insts:
    output.write("%s " %format(address,"#04x"))
    output.write(Mips_Decoder(item,address).PrintInst())
    output.write("\n")
    address+=4
    
output.close()   
    