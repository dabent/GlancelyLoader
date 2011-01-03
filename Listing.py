
class Inserter:

    def __init__(self, table):
        self.listings = []
        self.header = "INSERT INTO `" + table + "` (`id`,`listing_id`,`state`,`user_id`,`title`,`description`,`creation_tsz`,`ending_tsz`,`original_creation_tsz`,`last_modified_tsz`,`price`,`currency_code`,`quantity`,`tags`,`materials`,`shop_section_id`,`featured_rank`,`state_tsz`,`hue`,`saturation`,`brightness`,`is_black_and_white`,`url`,`views`,`url_75x75`,`url_170x135`,`url_570xN`,`url_fullxfull`,`keyset`,`created`,`color`,`merchant`,`shop`,`sorter`) VALUES \n"

    def rreplace(self, s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    def toString (self):
        line = self.header
        for listing in self.listings:
            line = line + listing.toString() + ",\n"

        line = self.rreplace(line,",",";",1)
        return line
    
class ProductRow:

    IMAGE_URL_BASE = "http://www.glancely.com/images/product/"
    
    def __init__(self):

        self.id = 0
        self.listingId = 0 # originally Etsy listing ID
        self.state = " " # "active" or "in stock" or something like that
        self.user_id = 0 # was Etsy user
        self.title = " "
        self.description = " "
        self.creation_tsz = 0.0
        self.ending_tsz = 0.0
        self.original_creation_tsz =0.0
        self.last_modified_tsz = 0.0
        self.price = 0.0
        self.currencyCode = " "
        self.quantity = 1
        self.tags = " "
        self.materials = " "
        self.shop_section_id = 0
        self.featured_rank = 0
        self.state_tsz = 0.0
        self.hue = 0
        self.saturation = 0
        self.brightness = 0
        self.is_black_and_white = False
        self.url = " "
        self.views = 0
        self.url_75x75 = " "
        self.url_170x135 = " "
        self.url_570xN = " "
        self.url_fullxfull = " "
        self.keyset = " "
        self.created = None
        self.color = 0
        self.merchant = " "
        self.shop = " "
        self.sorter = 0

    def toString(self):
        #    insertLine = "INSERT INTO `" + table + "` (`id`,`listing_id`,`state`,`user_id`,`title`,`description`,`creation_tsz`,`ending_tsz`,
        # `original_creation_tsz`,`last_modified_tsz`,`price`,`currency_code`,`quantity`
        # ,`tags`,`materials`,`shop_section_id`,`featured_rank`,`state_tsz`,`hue`,`saturation`,`brightness`,`is_black_and_white`
        # ,`url`,`views`,`url_75x75`,`url_170x135`
        # ,`url_570xN`,`url_fullxfull`,`keyset`,`created`,`color`,`merchant`,`shop`,`sorter`) VALUES \n"

        line = "(" + str(self.id) + "," + str(self.listingId) + ",'" + self.state + "'," + str(self.user_id) + ",'" + self.title
        line = line + "','" + self.description + "'," + str(self.creation_tsz) + "," + str(self.ending_tsz)
        line = line + "," + str(self.original_creation_tsz) + "," + str(self.last_modified_tsz)
        line = line + "," + str(self.price) + ",'" + self.currencyCode + "'," + str(self.quantity)
        line = line + ",'" + self.tags + "','" + self.materials + "'," + str(self.shop_section_id) + "," + str(self.featured_rank) + "," + str(self.state_tsz)
        line = line + "," + str(self.hue) + "," + str(self.saturation) + "," + str(self.brightness) + "," + "0" # for now assume all are black and white
        line = line + ",'" + self.url + "'," + str(self.views) + ",'" + self.IMAGE_URL_BASE + self.url_75x75 + "','" + self.IMAGE_URL_BASE + self.url_170x135
        line = line + "','" + "url_570xN" + "','" + "url_fullxfull" +  "','" + self.tags + " " + self.description + " " + self.title
        line = line + "'," + "NOW()" + "," + str(self.color) + ",' ','" + self.shop + "'," + str(self.sorter) + ")"
        
        return line

if __name__ == "__main__":

    pr = ProductRow()
    pr.id = 555

    pr2 = ProductRow()
    pr2.id = 222

    l = Inserter("listing2")

    l.listings.append(pr)
    l.listings.append(pr2)
    
    print l.toString()

        
