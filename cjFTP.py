from ftplib import FTP
import gzip
import os
import cjProductFeed
import thread

lines = []
retailers = [('Scarpasa', 100000, 0),('Linea', 120000,1),('GelaSkins',140000,2),('Kidorable',160000,3),('Diamond', 180000,4),('Jimmy',200000,5),('DNA',220000,6),('skechers',240000,7),('luxury',260000,8),('Keen',280000,9),('Stauer',300000,10),('dellamoda1',320000,11)]

class FTPFiler:
    def __init__(self, fileName):
        self.fileName = fileName
        self.ftp = None
        print 'Opening local file ' + self.fileName
        self.outFile = open("/tmp/" + self.fileName, 'wb')

    def getFile(self):
        ftp = FTP('datatransfer.cj.com')
        ftp.login('1789081','nkLUyuni')
        ftp.sendcmd('CWD /outgoing/productcatalog/70143')
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

def dumpline(line):
    print "The Line Is: " + line
    fileName = line.rsplit(";",1)[1].strip()
    print "The Filename is: " + fileName
    # Open the file for writing in binary mode
    ftpFile = FTPFiler(fileName)
    infile = ftpFile.getFile()
    for retailer in retailers:
        if fileName.find(retailer[0]) > -1:
            cjF = cjProductFeed.cjFeeder()
            print "The Filename is: " + infile + " retailer is " + retailer[0]
            thread.start_new_thread(cjF.buildSQLFile, ('listing', infile, retailer[0], retailer[1], retailer[2]))
#            cjProductFeed.buildSQLFile('listing', infile, '/tmp/'+retailer[0]+'.sql', retailer[1])
            break
    
def keepLine(line):
    lines.append(line)
    
if __name__ == "__main__":

    ftp = FTP('datatransfer.cj.com')
    ftp.login('1789081','nkLUyuni')
    ftp.sendcmd('CWD /outgoing/productcatalog/70143')
    ftp.retrlines('MLSD', keepLine)
    ftp.quit()
#    print lines
    for line in lines:
        dumpline(line)

    
