import os, sys
import Image
import urllib
import sys
import subprocess
import random
import imageAnalysis
import Listing

import traceback

import xml.etree.cElementTree as cElementTree
#from xml.dom import minidom

ALIGN_CENTER = 0
ALIGN_BOTTOM = 1

class cjFeeder:

    def __init__(self):
        self.thumbX = 75
        self.thumbY = 75
        self.bigX = 170
        self.bigY = 135

    def resize(self, limitX,limitY,image,filename,align):

        x = image.size[0]
        y = image.size[1]

        
        if (x < limitX) or (y < limitY):
            #print "IMAGE TOO SMALL for: " + filename
            return None
        else:

            result = True
            try:
                #resize/crop/What?
                newX = 0
                newY = 0
                if x > y:
                    newY = limitY
                    newX = x * limitY/y
                    #resize using Y as limit
                else:
                    newX = limitX
                    newY = y * limitX/x
            
                bigim = image.resize((newX,newY),Image.ANTIALIAS)

                # Then crop off excess of longer dimension.

                cropOffsetX = 0
                cropOffsetY = 0
                if newX > limitX:
                    cropOffsetX = (newX - limitX) / 2
                else:
                    if align == ALIGN_BOTTOM:
                        cropOffsetY = (newY - limitY)
                    else:
                        cropOffsetY = (newY - limitY) / 2
                    
                box = (cropOffsetX, cropOffsetY, cropOffsetX + limitX, cropOffsetY + limitY)

                bigim = bigim.crop(box)

                bigim.save(filename)
                result = True
            except:
                #print "some problem or another loading image: " + filename
                result = None

            return result
        
    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def pullImageAndGenThumbs(self, imageURL, id, retailerID):

        imageURLs = None
        infile = "/tmp/imagestore/" + str(id) + ".jpg"
        try:
            urlOpener = urllib.URLopener()
            urlOpener.retrieve(imageURL, infile)
        except:
            #print "Error Downloading: image: '" + imageURL + "'"
            return False
        
        try:
            im = Image.open(infile)
        except:
            #print "Error Opening: image: '" + infile + "'"
            return False
        #print infile, im.format, "%dx%d" % im.size, im.mode

        align = ALIGN_CENTER
        if (retailerID == 6) or (retailerID == 8): #DNA Shoes
            align = ALIGN_BOTTOM
        retBig = self.resize(self.bigX,self.bigY,im,"/tmp/images/product/" + str(id) + "_170x135.jpg", align)
        if retBig:
            retSmall = self.resize(self.thumbX,self.thumbY,im,"/tmp/images/product/" + str(id) + "_75x75.jpg", align)
            retBig = (str(id) + "_75x75.jpg", str(id) + "_170x135.jpg")
        else:
            return False

        return retBig
                
    def buildSQLFile(self, table, filename, retailer, count, retailerID):

        try:
            outname = "/tmp/" + retailer + ".sql"
            outname2 = "/tmp/" + retailer + "2.sql"
            print "Writing to: " + outname + " from: " + filename
            fout = open(outname, 'w')
            fout.write("USE etsy_instant;\n")
        #    fout.write("truncate table " + table + ";\n")
            fout.write("/*!40000 ALTER TABLE `" + table + "` DISABLE KEYS */;\n" )

#            xmldoc = minidom.parse(filename)
            # get an iterable
            context = cElementTree.iterparse(filename, events=("start", "end"))
            # turn it into an iterator
            context = iter(context)
            # get the root element
            event, root = context.next()

#            products = xmldoc.getElementsByTagName("product")
#            print "There are: " + str(products.length) + " products in " + filename

            #insertLine = "INSERT INTO `" + table + "` (`id`,`listing_id`,`state`,`user_id`,`title`,`description`,`creation_tsz`,`ending_tsz`,`original_creation_tsz`,`last_modified_tsz`,`price`,`currency_code`,`quantity`,`tags`,`materials`,`shop_section_id`,`featured_rank`,`state_tsz`,`hue`,`saturation`,`brightness`,`is_black_and_white`,`url`,`views`,`url_75x75`,`url_170x135`,`url_570xN`,`url_fullxfull`,`keyset`,`created`,`color`,`merchant`,`shop`,`sorter`) VALUES \n"

            insertLine = Listing.Inserter(table)
            
#            for product in products:
            for event, elem in context:
                if event == "end" and elem.tag == "product":
                    pr = Listing.ProductRow()

                    pr.id = count
                    pr.state = elem.findtext("instock") #self.getText(product.getElementsByTagName("instock")[0].childNodes)
                    title = elem.findtext("name").replace("'", "") #self.getText(product.getElementsByTagName("name")[0].childNodes).replace("'", "")
                    pr.title = title.replace('"', '')
                    pr.description = elem.findtext("description").replace("'", "") #self.getText(product.getElementsByTagName("description")[0].childNodes).replace("'", "")
                    pr.price = elem.findtext("price").replace("'", "") #self.getText(product.getElementsByTagName("price")[0].childNodes).replace(",", "")
                    pr.currency = elem.findtext("currency").replace("'", "") #self.getText(product.getElementsByTagName("currency")[0].childNodes)
                    pr.tags = elem.findtext("keywords").replace("'", "") #self.getText(product.getElementsByTagName("keywords")[0].childNodes).replace("'", "")
                    pr.url = elem.findtext("buyurl") #self.getText(product.getElementsByTagName("buyurl")[0].childNodes)
                    pr.shop = elem.findtext("programname").replace("'", "") #self.getText(product.getElementsByTagName("programname")[0].childNodes)
                    imageURL = elem.findtext("imageurl") #self.getText(product.getElementsByTagName("imageurl")[0].childNodes)
                    if imageURL:
                        imageURLs = self.pullImageAndGenThumbs(imageURL, count, retailerID)
                    if imageURLs == False:
                        continue

                    pr.url_75x75 = imageURLs[0]
                    pr.url_170x135 = imageURLs[1]
                    pr.color = imageAnalysis.calculateImageColor('/tmp/images/product/'+imageURLs[0])
                    
                    pr.sorter = random.getrandbits(64)

                    insertLine.listings.append(pr)
                    
                    if count % 25 != 0:
                        pass
                    else:
                        print ".",
                        try:
                            fout.write(insertLine.toString())
                        except UnicodeEncodeError:
                            pass
                            #print "Skipping unicode line for file " + filename
                        insertLine = Listing.Inserter(table)
                    
                    count = count + 1
                    root.clear()

            fout.write("/*!40000 ALTER TABLE `" + table + "` ENABLE KEYS */;\n")
            fout.close()
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print "Problem? " + outname + " from: " + filename
            print "*** print_tb:"
            traceback.print_tb(exceptionTraceback)
            print "*** print_exception:"
            traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback,
                                      limit=2, file=sys.stdout)
            print "*** print_exc:"
            traceback.print_exc()
            print "*** format_exc, first and last line:"
            formatted_lines = traceback.format_exc().splitlines()
            print formatted_lines[0]
            print formatted_lines[-1]
            print "*** format_exception:"
            print repr(traceback.format_exception(exceptionType, exceptionValue,
                                                  exceptionTraceback))
            print "*** extract_tb:"
            print repr(traceback.extract_tb(exceptionTraceback))
            print "*** format_tb:"
            print repr(traceback.format_tb(exceptionTraceback))
            print "*** tb_lineno:", traceback.tb_lineno(exceptionTraceback)

        print "DONE writing to: " + outname + " from: " + filename

        if sys.platform == "win32":
            process = subprocess.Popen(["/PROGRA~2/Git/bin/sh.exe", "-c", "/bin/sed 's/`listing`/`listing2`/' /c" + outname + " >/c" + outname2], shell=False, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        else:
            process = subprocess.Popen(["/bin/bash","-c","/bin/sed 's/`listing`/`listing2`/' " + outname + " >" +  outname2], shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE) #, stdout=subprocess.PIPE)

        print "DONE writing to: " + outname2 + " from: " + filename
##      except Exception as inst:
##            print type(inst)     # the exception instance
##            print inst.args      # arguments stored in .args
##            print inst           # __str__ allows args to printed directly


if __name__ == "__main__":

##    args = sys.argv[1:]
##
##    table = "listing"
##    filename = ""
##    count = 0
##    #usage: filename outname countbase <tablenumber>
##    #'C:\\Users\\Davin\\Downloads\\Diamond_com-Product_Catalog.xml'
##    print "I've got " + str(len(args)) + " args!"
##    if (len(args) == 4) or (len(args) == 3):
##        if len(args) == 4:
##            table = "listing2"
##        filename = args[0]
##        outname = args[1]
##        count = int(args[2])
##        print "Filename: " + filename + " count: " + str(count)
##    else:
##        print "Usage: python cyProductFeed.py infilename outfilename countbase tableid"
##        os._exit(1)
    cjF = cjFeeder()

    cjF.buildSQLFile('listing','/tmp/MacMall_Affiliate_Advantage_Network-Product_Catalog_1.xml','/tmp/MacMall.sql',210000)


    
