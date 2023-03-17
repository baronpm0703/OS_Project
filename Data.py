import binascii

class BootSectorFAT32:
    # Initiate Value, Atrribute
    def __init__(self) -> None:
        self.bytePerSector = 0
        self.sectorPerCluster = 0
        self.sectorBeforeFAT = 0
        self.cntFAT = 0
        self.sizeVol = 0
        self.sectorPerFAT = 0
        self.firstClusterinRDET = 0
        self.FATtypeEach = 0
        self.FATtype = ""
    
    # Read Boot Sector - Read 26 Bytes At First Sector
    def ReadBootSector(self, drive):
        
        with open(drive, 'rb') as fp:
            
            # First we move to Offset 0x0B
            fp.read(11)
            
            # Read: Byte per sector, Sector per cluster, Sector before FAT, Count of FAT
            self.bytePerSector = int.from_bytes(fp.read(2), byteorder='little') 
            self.sectorPerCluster = int.from_bytes(fp.read(1), byteorder='little')
            self.sectorBeforeFAT = int.from_bytes(fp.read(2), byteorder='little')
            self.cntFAT = int.from_bytes(fp.read(1), byteorder='little') # It End At 0x11
            
            # Next, we move to Offset 0x20
            fp.seek(15,1)
            # Read: Size of volume, Sector per FAT
            self.sizeVol = int.from_bytes(fp.read(4), byteorder='little')
            self.sectorPerFAT = int.from_bytes(fp.read(4), byteorder='little') # End At 0x28
            
            # Then we move to Offset 0x30
            fp.seek(4,1)
            # Read: First cluster in RDET
            self.firstClusterinRDET = int.from_bytes(fp.read(4), byteorder='little') #End At 0x30
            
            # Final, we move to Offset 0x52
            fp.seek(34,1)
            
            # Read: Each Byte of FAT type then convert to ASCII
            for i in range(8):
                self.FATtypeEach = int.from_bytes(fp.read(1), byteorder='little')
                self.FATtype += chr(self.FATtypeEach)
                
        return 0

    def PrintBootSector(self):
        
        print("Byte per sector: ", self.bytePerSector)
        print("Sector per cluster: ", self.sectorPerCluster)
        print("Sector before FAT: ", self.sectorBeforeFAT)
        print("Count of FAT: ", self.cntFAT)
        print("Size of volume: ", self.sizeVol)
        print("Sector per FAT: ", self.sectorPerFAT)
        print("First cluster in RDET: ", self.firstClusterinRDET)
        print("FAT type: ", self.FATtype)
    
        print("\n")
        
class MBR:
    def __init__(self) -> None:
        self.status = 0
        self.startAdd = 0
        self.patitionType = 0
        self.endAdd = 0
        self.startSector = 0
        self.totalSector = 0
        
    def readMBR(self, drive):
        with open(drive, 'rb') as fp:
            fp.read(446)
            self.status = hex(int.from_bytes(fp.read(1), byteorder = 'big'))
            self.startAdd = hex(int.from_bytes(fp.read(3), byteorder = 'big'))
            self.patitionType = hex(int.from_bytes(fp.read(1), byteorder = 'big'))
            self.endAdd = hex(int.from_bytes(fp.read(3), byteorder = 'big'))
            self.startSector = (int.from_bytes(fp.read(4), byteorder='little'))
            self.totalSector = (int.from_bytes(fp.read(4), byteorder='big'))
        return 0
    
    def PrintMBR(self):
        print("Status: ", self.status)
        print("Start Address: ", self.startAdd)
        print("Partition Type: ", self.patitionType)
        print("End Address: ", self.endAdd)
        print("Start Sector: ", hex(int(self.startSector)))
        print("Total Sector: ", self.totalSector)

class Entry: # These just Object to store data of each Entry

    def __init__(self) -> None:
        self.name = ""
        self.attr = ""
        self.attr_Bin = 0
        self.createTime = 0
        self.createDate = 0
        self.size = 0
        self.startCluster = 0
        self.tempName = ""
        
        self.NextENTRY = None #IF IT IS A DIRECTORY, IT WILL HAVE NEXT ENTRY
        
    def setNULL(self):
        self.name = ""
        self.attr = ""
        self.attr_Bin = 0
        self.createTime = 0
        self.createDate = 0
        self.startCluster = 0
        self.size = 0
        self.tempName = ""

    def PrintAttribute(self):
        
        print("Name: ", self.name)
        #print("Bit Pattern of Attribute: ", self.attr_Bin)
        print("Attribute: ", self.attr)
        print("Create Time: ", self.createTime)
        print("Create Date: ", self.createDate)
        print("Start Cluster: ", self.startCluster)
        print("Size: ", self.size)

        print('\n')

class RDET:
    
    # We Read Each Entry And Store It In List
    def __init__(self) -> None:
        self.ListEntry = []
        self.EachEntry = None
    
    def ReadMainEntry(self, address, drive, fp):
                #seek(1,0) -> ten chinh
                #read tung byte
                fp.seek(address,0)
                if(self.EachEntry.name == ""):
                    for i in range(8):
                        eachName  = fp.read(1)
                        #eachName  = int.from_bytes(fp.read(1), byteorder='little')
                        if eachName.decode('ascii') != ' ': # If not space
                            self.EachEntry.name += eachName.decode('ascii')
                    
                    #read(3) -> ten phu
                    self.EachEntry.name += "."
                    for i in range(3):
                        eachName  = fp.read(1)
                        #eachName  = int.from_bytes(fp.read(1), byteorder='little')
                        self.EachEntry.name += eachName.decode('ascii')
                else:
                    fp.seek(11,1)
                #read(1) -> attribute
                getbinary = lambda x, n: format(x, 'b').zfill(n)
                self.EachEntry.attr_Bin = getbinary(int.from_bytes(fp.read(1), byteorder = 'little'),8)
                bi = self.EachEntry.attr_Bin
                for i in range(len(bi)):
                    if bi[i] == '1':
                        if i==2:
                            self.EachEntry.attr += "Archive, "
                        elif i==3:
                            self.EachEntry.attr += "Directory, "
                        elif i==4:
                            self.EachEntry.attr += "Volume Label, "
                        elif i==5:
                            self.EachEntry.attr += "System File, "
                        elif i == 6:
                            self.EachEntry.attr += "Hidden File, "
                        elif i==7:
                            self.EachEntry.attr += "Read Only, "
                #seek(1) -> seek 1
                #read(1) -> create time
                fp.seek(1,1)
                time = getbinary((int.from_bytes(fp.read(3),'little')), 24)
                self.EachEntry.createTime = str(int(time[0:5],2)) + ":" + str(int(time[5:11],2)) + ":" + str(int(time[11:16],2))
                #read(4) -> create date time
                date = getbinary((int.from_bytes(fp.read(2),'little')), 16)
                self.EachEntry.createDate = str(int(date[11:16],2)) + "/"+ str(int(date[7:11],2)) + "/" + str(int(date[0:7],2)+1980)
                #seek(10)
                fp.seek(8,1)
                self.EachEntry.startCluster = int.from_bytes(fp.read(2),byteorder='little')
                #read(4) -> size
                self.EachEntry.size = int.from_bytes(fp.read(4),byteorder='little')
                
    #read entry phu
    def ReadExtraEntry(self, address, drive, fp):
            #seek(1)
            fp.seek(address,0)
            fp.seek(1,1)
            #read(10) -> 5 ky tu cua ten file utf-16
 
            for i in range(5):
                eachName  = fp.read(2)
                if eachName.decode('utf-16') != ' ':
                    self.EachEntry.tempName += eachName.decode('utf-16')
            #seek(3)
            fp.seek(3,1)
            #read(12)-> 6 ky tu ten file
            for i in range(6):
                eachName = fp.read(2)
                if eachName.decode('utf-16') != ' ':
                    self.EachEntry.tempName += eachName.decode('utf-16')
            #seek(2)
            fp.seek(2,1)
            #read(4) -> 2 ky tu ten file
            for i in range(2):
                eachName = fp.read(2)
                if eachName.decode('utf-16') != ' ':
                    self.EachEntry.tempName += eachName.decode('utf-16')

    def PrintRDET(self):

        for i in self.ListEntry:
            i.PrintAttribute()
    
    def ReadRDET(self,address, drive):
        # Step_1: Move to offset xxxB (1 byte): check the type of Entry
        # Step_2: If it is Main Entry, read 32 bytes
        # Otherwise, read Extra Entry
        # Step_3: Move another 32 Byte with Address and repeat Step_1
        
        with open (drive, 'rb') as fp:
            TempName = ""
            while True:
                # New Entry Each Time
                self.EachEntry = Entry()
                
                # Seek each Entry - 32 bytes pattern
                fp.seek(address,0)
                
                if int.from_bytes(fp.read(1), byteorder='little') == 0xE5:  
                    address += 32         
                    continue
                # Move to offset 11B (1 byte): check the type of Entry
                fp.read(10)
                
                getbinary = lambda x, n: format(x, 'b').zfill(n) # Full Fill The Binary Pattern with n bit
                first_Byte_Main_Entry = int.from_bytes(fp.read(1), byteorder='little') 
                
                if first_Byte_Main_Entry == 0: break # Empty Entry -> End Of Directory
                if  first_Byte_Main_Entry == 15: # Extra Entry
                    self.ReadExtraEntry(address, drive, fp)
                    
                    self.EachEntry.name = self.EachEntry.tempName + self.EachEntry.name
                    TempName = self.EachEntry.name + TempName
                else:
                    self.ReadMainEntry(address, drive, fp)
                    if (TempName != ""):
                        self.EachEntry.name = TempName
                        TempName = ""
                    self.ListEntry.append(self.EachEntry)
                address += 32
        return 0

