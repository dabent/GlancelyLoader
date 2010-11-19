import os, sys
import Image
import urllib
import sys
import random

from xml.dom import minidom

def resize(bigX,bigY,image,filename):
    x = image.size[0]
    y = image.size[1]

    if (x < bigX) or (y < bigY):
        print "IMAGE TOO SMALL"
        return None
    else:

        #resize/crop/What?
        newX = 0
        newY = 0
        if x > y:
            newY = bigY
            newX = x * bigY/y
            #resize using Y as limit
        else:
            newX = bigX
            newY = y * bigX/x
    
        bigim = image.resize((newX,newY),Image.ANTIALIAS)

        # Then crop off excess of longer dimension.

        cropOffsetX = 0
        cropOffsetY = 0
        if newX > bigX:
            cropOffsetX = (newX - bigX) / 2
        else:
            cropOffsetY = (newY - bigY) / 2
            
        box = (cropOffsetX, cropOffsetY, cropOffsetX + bigX, cropOffsetY + bigY)

        bigim = bigim.crop(box)

        bigim.save(filename)
        return True

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def pullImageAndGenThumbs(imageURL, id):

    imageURLs = None
#    try:
    urlOpener = urllib.URLopener()
    urlOpener.retrieve(imageURL, "C:\\Users\\Davin\\Downloads\\images\\" + str(id) + ".jpg")
    
    infile = "C:\\Users\\Davin\\Downloads\\images\\" + str(id) + ".jpg"

    im = Image.open(infile)
    #print infile, im.format, "%dx%d" % im.size, im.mode

    retBig = resize(bigX,bigY,im,"C:\Users\Davin\Downloads\images\\thumbs\\" + str(id) + "_170x135.jpg")
    if retBig:
        retSmall = resize(thumbX,thumbY,im,"C:\Users\Davin\Downloads\images\\thumbs\\" + str(id) + "_75x75.jpg")
        retBig = (str(id) + "_75x75.jpg", str(id) + "_170x135.jpg")

    return retBig
#    except:
#        print "Error Downloading: image: '" + imageURL + "'"
            
if __name__ == "__main__":

    args = sys.argv[1:]

    table = "listing"
    filename = ""
    count = 0
    #usage: filename countbase <tablenumber>
    #'C:\\Users\\Davin\\Downloads\\Diamond_com-Product_Catalog.xml'
    if (len(args) == 2) or (len(args) == 3):
        print "I've got " + str(len(args)) + " args!"
        if len(args == 3)
            table = "listing2"
        filename = args[0]
        count = int(args[1])
        print "Filename: " + filename + " count: " + str(count)
    else:
        print "No Args"
        os._exit(n)

    thumbX = 75
    thumbY = 75

    bigX = 170
    bigY = 135

    fout = open('/tmp/workfileCJ.sql', 'w')
    fout.write("USE etsy_instant;\n")
#    fout.write("truncate table " + table + ";\n")
    fout.write("/*!40000 ALTER TABLE `" + table + "` DISABLE KEYS */;\n" )

    xmldoc = minidom.parse(filename)
    products = xmldoc.getElementsByTagName("product")

    print "There are: " + str(products.length) + " products"

    insertLine = "INSERT INTO `" + table + "` (`id`,`listing_id`,`state`,`user_id`,`title`,`description`,`creation_tsz`,`ending_tsz`,`original_creation_tsz`,`last_modified_tsz`,`price`,`currency_code`,`quantity`,`tags`,`materials`,`shop_section_id`,`featured_rank`,`state_tsz`,`hue`,`saturation`,`brightness`,`is_black_and_white`,`url`,`views`,`url_75x75`,`url_170x135`,`url_570xN`,`url_fullxfull`,`keyset`,`created`,`color`,`merchant`,`shop`,`sorter`) VALUES \n"

    for product in products:
        #print product.getElementsByTagName("name")
        
        instock = getText(product.getElementsByTagName("instock")[0].childNodes)
        title = getText(product.getElementsByTagName("name")[0].childNodes).replace("'", "")
        title = title.replace('"', '')
        description = getText(product.getElementsByTagName("description")[0].childNodes).replace("'", "")
        price = getText(product.getElementsByTagName("price")[0].childNodes).replace(",", "")
        currency = getText(product.getElementsByTagName("currency")[0].childNodes)
        tags = getText(product.getElementsByTagName("keywords")[0].childNodes).replace("'", "")
        url = getText(product.getElementsByTagName("buyurl")[0].childNodes)
        shopName = getText(product.getElementsByTagName("programname")[0].childNodes)
        imageURL = getText(product.getElementsByTagName("imageurl")[0].childNodes)
        imageURLs = pullImageAndGenThumbs(imageURL, count)
        url_75x75 = imageURLs[0]
        url_170x135 = imageURLs[1]
        
        insertLine = insertLine + "(" + str(count) + "," + str(0) + ",'" + "active" + "'," + str(0) + ",'" + title
        insertLine = insertLine + "','" + "description" + "'," + str(0) + "," + str(0)
        #`original_creation_tsz`,`last_modified_tsz`,
        insertLine = insertLine + "," + str(0) + "," + str(0)
        #`price`,`currency_code`,`quantity`,
        insertLine = insertLine + "," + str(price) + ",'" + currency + "'," + str(1)
        #`tags`,`materials`,`shop_section_id`,`featured_rank`,`state_tsz`,`hue`,`saturation`,`brightness`,`is_black_and_white`,
        insertLine = insertLine + ",'" + tags + "','" + " " + "'," + "0" + "," + "0" + "," + "0" + "," + "0" + "," + "0" + "," + "0" + "," + "0"
        #`url`,`views`,`url_75x75`,`url_170x135`,`url_570xN`,`url_fullxfull`,`keyset`,`created`,`color`,`merchant`,`shop`) VALUES \n"
        insertLine = insertLine + ",'" + url
        insertLine = insertLine + "'," + str(0)
        insertLine = insertLine + ",'" + "http://www.glancely.com/images/product/" + url_75x75
        insertLine = insertLine + "','" + "http://www.glancely.com/images/product/" + url_170x135
        insertLine = insertLine + "','" + "url_570xN"
        insertLine = insertLine + "','" + "url_fullxfull"
        insertLine = insertLine +  "','" + tags + " " + description + " " + title
        insertLine = insertLine + "'," + "NOW()"
        insertLine = insertLine + ",0"
        insertLine = insertLine + ",' ','" + shopName + "'," + str(random.getrandbits(64))
        if count % 25 != 0:
            insertLine = insertLine + "),\n"
        else:
            print count
            insertLine = insertLine + ");\n"
            fout.write(insertLine)
            insertLine = "INSERT INTO `" + table + "` (`id`,`listing_id`,`state`,`user_id`,`title`,`description`,`creation_tsz`,`ending_tsz`,`original_creation_tsz`,`last_modified_tsz`,`price`,`currency_code`,`quantity`,`tags`,`materials`,`shop_section_id`,`featured_rank`,`state_tsz`,`hue`,`saturation`,`brightness`,`is_black_and_white`,`url`,`views`,`url_75x75`,`url_170x135`,`url_570xN`,`url_fullxfull`,`keyset`,`created`,`color`,`merchant`,`shop`,`sorter`) VALUES \n"

        count = count + 1

    fout.write("/*!40000 ALTER TABLE `" + table + "` ENABLE KEYS */;\n")
    fout.close()



    
