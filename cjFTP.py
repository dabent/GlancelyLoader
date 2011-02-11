from ftplib import FTP
import gzip
import os
import cjProductFeed
import thread
import sys

SUBDIR = '74204'

lines = []
retailers = [('Scarpasa', 100000, 0),('Linea', 120000,1),('GelaSkins',140000,2),('Kidorable',160000,3),('Diamond', 180000,4),
             ('Jimmy',200000,5),('DNA',220000,6),('skechers',240000,7),('luxury',260000,8),('Keen',280000,9),('Stauer',300000,10),
             ('dellamoda1',320000,11),('Birkenstock',340000,12),('Koolaburra',360000,13),('JewelsForMe',380000,14),('Fashion58',400000,15),
             ('Cashmere',420000,16), ('Pure',440000,17),('alwaysforme',460000,18),('n_fini',480000,19),('hessnatur',500000,20),
             ('Womensuits',520000,21), ('Willow_Ridge',540000,22),('TheHipChick',560000,23),('Singer22',580000,24),('Silkies',600000,25),
             ('Monterey_Bay',620000,26), ('Michael_Stars',640000,27),('House_of_Brides',660000,28),('Fashion_Specialists',680000,29),('ChicStar',700000,30),
             ('Bedford_Fair',720000,31), ('Amiclubwear',740000,32),('M_Fredric',760000,33),('Allsaints',780000,34), ('MegaSuits',800000,35),
             ('Mountain_Retail',820000,36),('StylinOnline',840000,37),('universalgear',860000,38),('WildAttire-Neckties',880000,39), ('WebUndies',900000,40),
             ('Austad',920000,41), ('alight_Product',940000,42),('Bluegala_Product',960000,43),('Charm_Chain',980000,44), ('etnies',1000000,45),
             ('eWatches',1020000,46),('FineJewelers',1040000,47),('Finishline',1060000,48),('GoldenMine_Product',1080000,49), ('Heavenly_Treasures',1100000,50),
             ('Heavenly_Treasures',1120000,51), ('Jack_Schwartz',1140000,52),('Sneaux_Shoes',1160000,53),('PalmBeachJewelry',1180000,54), ('Sea_of_Diamonds',1200000,55),
             ('Dansko',1320000,56),('NAOT',1340000,57),('Sun_Jewelry',1360000,58),('Time_and_Gems',1380000,59), ('Diamond_Harmony',1400000,60),
             ('Banana_Republic',1420000,61), ('Gap-Product',1440000,62),('Old_Navy',1460000,63)
             ]

class FTPFiler:
    def __init__(self, fileName):
        self.fileName = fileName
        self.ftp = None
        print 'Opening local file ' + self.fileName
        self.outFile = open("/tmp/" + self.fileName, 'wb')

    def getFile(self):
        ftp = FTP('datatransfer.cj.com')
        ftp.login('1789081','nkLUyuni')
        ftp.sendcmd('CWD /outgoing/productcatalog/'+ SUBDIR)
        ftp.retrbinary('RETR ' + self.fileName, self.handleDownload)
        self.outFile.close()
        ftp.sendcmd('DELE ' + self.fileName)
        ftp.quit()
        f = gzip.open("/tmp/" + self.fileName, 'rb')
        file_content = f.read()
        f.close()
        uncompressed = open("/tmp/" + self.fileName[0:len(self.fileName)-3], 'wb')
        uncompressed.write(file_content)
        uncompressed.close()

        os.remove("/tmp/" + self.fileName)

        return "/tmp/" + self.fileName[0:len(self.fileName)-3]
        
    # This will handle the data being downloaded
    # It will be explained shortly
    def handleDownload(self, block):
        self.outFile.write(block)
        print ".",

def dumpline(line, fileIWant):
    #print "The Line Is: " + line
    fileName = line.rsplit(";",1)[1].strip()
    #print "The Filename is: " + fileName

    if (fileName == fileIWant):
        # Open the file for writing in binary mode
        ftpFile = FTPFiler(fileName)
        infile = ftpFile.getFile()
        for retailer in retailers:
            if fileName.find(retailer[0]) > -1:
                cjF = cjProductFeed.cjFeeder()
                print "The Filename is: " + infile + " retailer is " + retailer[0]
                # thread.start_new_thread(cjF.buildSQLFile, ('listing', infile, retailer[0], retailer[1], retailer[2]))
                cjF.buildSQLFile('listing', infile, retailer[0], retailer[1], retailer[2])
                break
    
def keepLine(line):
    lines.append(line)
    
if __name__ == "__main__":

    args = sys.argv[1:]

    #ALERT - arg0 is subdir - arg 1 is filename.
    # no more threading, only retrieve on matched file name - EASY!  Do it sunday
    # set up 100 cron jobs and be done with this. Just dupe over cron jobs - EASY
    SUBDIR = args[0]
    fileName = args[1]
    
    ftp = FTP('datatransfer.cj.com')
    ftp.login('1789081','nkLUyuni')
    ftp.sendcmd('CWD /outgoing/productcatalog/' + SUBDIR)
    ftp.retrlines('MLSD', keepLine)
    ftp.quit()
#    print lines
    for line in lines:
        dumpline(line, fileName)
