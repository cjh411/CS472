# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 18:08:42 2017

@author: christopherhedenberg
"""

import numpy as np

MainMem=np.zeros(2048)
for i in range(2048):
    MainMem[i] = (i%(0xFF+1))
    
class Cache():
    def __init__(self,slot):
        self.vbit=0
        self.tag=0
        self.dirty = 0
        self.data=[0 for i in range(16)]
        
        
        
cache=[Cache(i) for i in range(16)] 

def cacheRead(address):
    slot = (address>>4)&0b000000001111
    tag = (address>>8)&0b000000001111
    offset= address&0b000000001111
    start=address&0b111111110000
    if cache[slot].vbit==1 and cache[slot].tag==tag:
        return ("At address %s is value %s  (Cache Hit)\n" %(format(address,'#04x'),format(int(cache[slot].data[offset]),'#04x')))
    elif cache[slot].vbit==1 and cache[slot].tag!=tag:
        if cache[slot].dirty==1:
            MemStart = (cache[slot].tag<<8)|(slot<<4)|(0b000000000000)
            for i in range(MemStart,MemStart+16):
                MainMem[i]=cache[slot].data[i-MemStart]
            cache[slot].dirty=0
        for i in range(start,start+16):
            cache[slot].data[i-start]=MainMem[i]
        cache[slot].vbit=1
        cache[slot].tag=tag
        return ("At address %s is value %s (Cache Miss)\n" %(format(address,'#04x'),format(int(cache[slot].data[offset]),'#04x')))
    else:
        cache[slot].vbit=1
        cache[slot].tag=tag
        for i in range(start,start+16):
            cache[slot].data[i-start]=MainMem[i]
        return ("At address %s is value %s (Cache Miss)\n" %(format(address,'#04x'),format(int(cache[slot].data[offset]),'#04x')))
                
def cacheWrite(address,value):
    slot = (address>>4)&0b000000001111
    tag = (address>>8)&0b000000001111
    offset= address&0b000000001111 
    if cache[slot].vbit==1 and cache[slot].tag==tag:
        cache[slot].data[offset] = value
        cache[slot].dirty=1
        return ("At address %s is value %s (Cache Hit)\n" %(format(address,'#04x'),format(int(cache[slot].data[offset]),'#04x')))
    elif cache[slot].vbit==1 and cache[slot].tag!=tag:
        cacheRead(address)
        cache[slot].data[offset] = value
        cache[slot].dirty=1
        return ("At address %s is value %s (Cache Miss)\n" %(format(address,'#04x'),format(int(cache[slot].data[offset]),'#04x')))
    else:
        cacheRead(address)
        cache[slot].data[offset] = value
        cache[slot].dirty=1
        return ("At address %s is value %s (Cache Miss)\n" %(format(address,'#04x'),format(int(cache[slot].data[offset]),'#04x')))

def cachePrint():
    display = 'Slot Valid Tag  Dirty Data\n'
    for item in range(len(cache)):
        datastr=''
        for element in cache[item].data:
            datastr=datastr+format(int(element),'#04X').ljust(5)
        display = display + "%s %s %s %s %s\n" %(format(item,'#04x').ljust(4),str(cache[item].vbit).ljust(5),format(cache[item].tag,'#04x').ljust(4),str(cache[item].dirty).ljust(5),datastr)          
    return display
        
CacheInput = open('/Users/christopherhedenberg/Downloads/courses/Architecture/Project2Input.txt','r').read().split('\n')
CacheOutput = open('/Users/christopherhedenberg/Downloads/courses/Architecture/Project2Output.txt','w')
i=0
CacheOutput.write("Chris Hedenberg\nCS472 Project 2 Output\n\n")
for item in CacheInput:
    CacheOutput.write("\n")
    if item == 'R':
        CacheOutput.write("(R)ead, (W)rite, or (D)isplay Cache?\nR\nAt which address?\n%s\n"%CacheInput[i+1]) 
        CacheOutput.write(cacheRead(int(CacheInput[i+1],16)))
        i+=2
    elif item=='W':
        CacheOutput.write("(R)ead, (W)rite, or (D)isplay Cache?\nW\nAt which address?\n%s\nWhat value?\n%s\n"%(CacheInput[i+1],CacheInput[i+2])) 
        CacheOutput.write(cacheWrite(int(CacheInput[i+1],16),int(CacheInput[i+2],16)))
        i+=3
    elif item=='D':
        CacheOutput.write("(R)ead, (W)rite, or (D)isplay Cache?\nD\n")
        CacheOutput.write(cachePrint())
        i+=1
    else:
        continue
    
CacheOutput.close()   


    
