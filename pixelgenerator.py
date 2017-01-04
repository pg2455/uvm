# city (String)
# domain (String)
# country (String)
# age (String)
# s_time (String)
# subscriber (String)
# s_id (String)
# frequency (String)
# gender (String)
# device (String)
# repeat_visitor (String)
# s_depth (Int)
# c_type (String)
# pv_depth (Int)
# pv_id (String)
# pv_time (Int)
# p_vendor (String)
# p_gain (Float)
# p_id (String)
# p_name (String)
# p_type (String)
# event (String)

products = [
    {"id": 1, "s":True, "type":"Video", "vendor":"Hearst", "name": "Instream Video", "gain":0.01, "success_rate":70, "f_cap":False, "intrusiveness":10, "mobile_success_rate":10, "min_depth":1}, 
    {"id": 2, "s":True, "type":"Display", "vendor":"Hearst", "name": "Display 300x250", "gain":0.002, "success_rate":80, "f_cap":False, "intrusiveness":5, "mobile_success_rate":45, "min_depth":1}, 
    {"id": 3, "s":True, "type":"Display", "vendor":"Hearst", "name": "Display 728x90", "gain":0.003, "success_rate":80, "f_cap":False, "intrusiveness":5,  "mobile_success_rate":0, "min_depth":1}, 
    {"id": 4, "s":True, "type":"Display", "vendor":"Hearst", "name": "Display 160x600", "gain":0.003, "success_rate":80, "f_cap":False, "intrusiveness":5,  "mobile_success_rate":0, "min_depth":1},
    {"id": 5, "s":False, "type":"Partner Ads", "vendor":"Genesis", "name": "Genesis Outstream", "gain":0.01, "success_rate":50, "f_cap":True, "intrusiveness":20,  "mobile_success_rate":0, "min_depth":2},  
    {"id": 6, "s":False, "type":"Partner Ads", "vendor":"Undertone", "name": "Undertone Interstitial", "gain":0.008, "success_rate":60, "f_cap":True, "intrusiveness":30,  "mobile_success_rate":0, "min_depth":2},
    {"id": 7, "s":False, "type":"Paywall", "vendor":"Piano", "name": "Piano Paywall", "gain":8.00, "success_rate":0.1, "f_cap":True, "intrusiveness":0,  "mobile_success_rate":0.05, "min_depth":4}, 
    {"id": 8, "s":True, "type":"Content Recommendation", "vendor":"Outbrain", "name": "Outbrain CR", "gain":0.003, "success_rate":3, "f_cap":True, "intrusiveness":50,  "mobile_success_rate":3, "min_depth":1}, 
    {"id": 9, "s":True, "type":"Content Recommendation", "vendor":"Taboola", "name": "Taboola CR", "gain":0.003, "success_rate":3, "f_cap":True, "intrusiveness":50,  "mobile_success_rate":3, "min_depth":1}]

sites = {"chron":{"domain":"chron.com", "sub_rate":3, "mobile":40, "first_market":"Houston", "second_markets":["San Antonio", "Austin", "Dallas", "Fort Worth"]},"sfgate":{"domain":"sfgate.com", "sub_rate":4, "mobile":60, "first_market":"San Francisco", "second_markets":["Los Angeles", "San Diego", "San Jose", "Fresno"]}}

import random
from random import randrange
import uuid
import urllib
import urllib2

def w_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w >= r:
         return c
      upto += w
   assert False, "Shouldn't get here"
   
class SessionGen:
  
  def __init__(self):
    
    self.site = sites[w_choice([["chron",55],["sfgate",45]])]
    self.products = products
    self.params = {}
    self.params["s_id"] = str(uuid.uuid4())
    self.params["domain"] = self.site["domain"]
    self.base_url = "http://gmpx.bzgint.com/collectorx/hearst/data/?tpc=hst&"
    self.mobile = False
    self.subscriber = False
    self.likely_depth = 1
    
    self.set_session_params()
    self.build_session_map()
    self.process_pixels()
    
  def set_session_params(self):
    #Device
    if randrange(101) < self.site["mobile"]:
      self.mobile = True
      self.params["device"] = "Mobile"
    else:
      self.mobile = False
      self.params["device"] = "Desktop"
    
    self.set_geo()
    self.set_user()
  
  def set_geo(self):
    #Country
    self.params["country"] = "United States"
    #City
    f = self.site["first_market"]
    s = random.choice(self.site["second_markets"])
    o = random.choice(["New York","Los Angeles","Chicago","Houston","Philadelphia","Phoenix","San Antonio","San Diego","Dallas","San Jose", "Austin","Jacksonville","San Francisco","Indianapolis","Columbus","Fort Worth", "Charlotte"])
    city_choices = [[f,75],[s,10],[o,15]]
    self.params["city"] = w_choice(city_choices)
     
  def set_user(self):
    #Subscriber, Repeat, Frequency
    if randrange(101) < self.site["sub_rate"]:
      self.subscriber = True
      # paywalls not allowed, more pages per visit
      self.params["subscriber"] = "true"
      self.params["repeat_visitor"] = "Yes"
      self.params["frequency"] = w_choice([["Infrequent",1],["Weekly", 6], ["Daily", 2]])
      self.params["gender"] = random.choice(["Male","Female"])
      self.params["age"] = w_choice([["18 to 25",10],["26 to 30",20],["31 to 40", 30], ["Over 40", 40]])
      self.likely_depth = w_choice([[1,3],[2,6],[3,6],[4,3],[5,3],[6,2],[7,1],[8,1]])
      
    else:
      self.subscriber = False
      self.params["subscriber"] = "false"
      r = w_choice([["Yes", 40], ["No", 60]])
      self.params["repeat_visitor"] = r
      if self.params["repeat_visitor"] is "Yes":
        self.params["frequency"] = w_choice([["Infrequent",85],["Weekly", 12],["Daily", 3]])
      else:
        self.params["frequency"] = "Not Available"
      
      self.params["gender"] = "Not Available"
      self.params["age"] = "Not Available"
      self.likely_depth = w_choice([[1,50],[2,30],[4,10],[5,5],[6,2],[7,2],[9,1]])
      if self.mobile is True:    
        self.likely_depth = w_choice([[1,70],[2,15],[4,7],[5,3],[6,2],[7,2],[9,1]])    
      
      
    if self.mobile is True and self.subscriber is False:
      self.likely_depth = w_choice([[1,70],[2,25],[4,5]])
  
  def build_session_map(self):
    current_depth = 1
    self.session_map = {}
    # print " "
    # print self.params["device"] + " : " + self.params["subscriber"]
    while current_depth <= self.likely_depth:
      early_termination_likelihood = 0
      paywall_shown = False
      pp = self.get_page_params()
      pm = {"pv_id":str(uuid.uuid4()), "depth":current_depth, "loaded":[], "succeeded":[], "atsop":pp["a"], "c_type":pp["v"]}
      products_loaded = self.eligible_products(current_depth)
      for p in products_loaded:
        pm["loaded"].append(p)
        if p["id"] is 7:
          paywall_shown = True
          
      for p in products_loaded:
        paywall_fail = False
        sr = p["success_rate"]
        if self.mobile:
          sr = p["mobile_success_rate"]
        did_succeed = w_choice([[True, sr],[False, 100-sr]])
        if did_succeed:
          pm["succeeded"].append(p)
          early_termination_likelihood = early_termination_likelihood + p["intrusiveness"]
        if p["id"] == 7 and not did_succeed:
          paywall_fail =  True
      
      self.session_map[current_depth] = pm
      

      
      string = "Depth " + str(current_depth) + " : " + "Loaded " + str(len(self.session_map[current_depth]["loaded"])) + " : " + "Success " + str(len(self.session_map[current_depth]["succeeded"])) + " : ETL " + str(early_termination_likelihood)
      
      
      
      current_depth = current_depth+1
      if paywall_fail:
        current_depth = self.likely_depth + 1
        string = string + " : SUBSCRIPTION FAIL"
      bouncing = w_choice([[True, early_termination_likelihood],[False, 100-early_termination_likelihood]])
      if self.params["subscriber"] is "true":
        if bouncing and early_termination_likelihood>=50:
          current_depth = self.likely_depth + 1
          string = string + " : INTERRUPTIVITY BOUNCE"
      else:
        if bouncing and early_termination_likelihood>25:
          current_depth = self.likely_depth + 1
          string = string + " : INTERRUPTIVITY BOUNCE"
      self.params["s_depth"] = len(self.session_map)
      s_time= 0
      for k in self.session_map:
        s_time = s_time + self.session_map[k]['atsop'];
      
      self.params["s_time"] = int(s_time)
      # print string
        
  def eligible_products(self, depth):
    if self.mobile:
      device_eligible = [p for p in self.products if p["mobile_success_rate"]>0.0]
    else:
      device_eligible = [p for p in self.products]
    
    if self.subscriber:
      user_eligible = [p for p in device_eligible if p["s"] is True]
    else:
      user_eligible = device_eligible
      
    depth_eligible = [p for p in user_eligible if depth >= p["min_depth"]]
    
    cap_eligible = []
    for i in xrange(0, len(depth_eligible)):
      p = depth_eligible[i]
      if p["f_cap"] is False:
        cap_eligible.append(p)
    
    cap_eligible.append(random.choice([self.products[7], self.products[8]]))
    
    if self.params["subscriber"] is "false":
      if depth is 4:
        cap_eligible.append(self.products[6])
      if depth is 2:
        cap_eligible.append(random.choice([self.products[5], self.products[4]]))
    
      
    return cap_eligible
    
  def get_page_params(self):
    verticals = ["News", "Business", "Sports", "Entertainment", "Food", "Living", "Travel", "Real Estate", "Cars", "Jobs", "Classifieds"]
    atsop_choices = [[0,9124],
    [3100,4596],
    [6200,3117],
    [9300,2286],
    [12400,1666],
    [15500,1469],
    [3200,1268],
    [18600,1148],
    [21700,1093],
    [6300,1080],
    [24800,997],
    [3000,956],
    [31000,857],
    [27900,844],
    [9400,820],
    [12500,749],
    [6100,729],
    [34100,719],
    [37200,693],
    [40300,645],
    [15600,642],
    [2900,573],
    [46500,560],
    [9200,554],
    [43400,550],
    [18700,531],
    [49600,493],
    [2300,490],
    [52700,488],
    [21800,485],
    [1800,470],
    [2800,468],
    [2500,462],
    [12300,460],
    [55800,460],
    [2100,454],
    [2700,454],
    [1600,451],
    [28000,450],
    [1900,444],
    [2200,444],
    [1200,429],
    [2000,426],
    [2400,424],
    [24900,423],
    [1500,419],
    [58900,413],
    [1300,412],
    [34200,411],
    [2600,410],
    [3300,405],
    [1400,402],
    [1700,402],
    [6400,398],
    [65100,394],
    [6000,392],
    [31100,387],
    [62000,386],
    [15400,369],
    [37300,356],
    [18500,353],
    [4600,343],
    [9500,342],
    [1100,338],
    [71300,338],
    [40400,335],
    [900,332],
    [4200,326],
    [12600,326],
    [77500,326],
    [68200,322],
    [1000,314],
    [74400,314],
    [4300,311],
    [9100,308],
    [4900,305],
    [4800,304],
    [24700,303],
    [4500,299],
    [4700,298],
    [5300,298],
    [5900,298],
    [46600,293],
    [83700,288],
    [5000,287],
    [4400,286],
    [5200,286],
    [15700,285],
    [43500,282],
    [80600,279],
    [800,278],
    [49700,274],
    [21600,273],
    [18800,269],
    [5400,267],
    [28100,264],
    [5700,263],
    [5600,259],
    [21900,259],
    [55900,259]]
    
    v = random.choice(verticals)
    a = w_choice(atsop_choices)
    
    return({"v":v,"a":a/(1000)})
  
  def get_pv_params(self, page_map):
    pv_params = {}
    pv_params["c_type"] = page_map["c_type"]
    pv_params["pv_id"] = page_map["pv_id"]
    pv_params["pv_time"] = int(page_map["atsop"])
    
    if self.mobile is True:
      pv_params["pv_time"] = int(page_map["atsop"]*.65)
    
    pv_params["pv_depth"] = page_map["depth"]
    return pv_params
    
  def get_product_opportunity_params(self, product_map):
    p_params = {}
    p_params["p_id"] = product_map["id"]
    p_params["p_vendor"] = product_map["vendor"]
    p_params["p_type"] = product_map["type"]
    p_params["p_name"] = product_map["name"]
    p_params["p_gain"] = 0.00
    return p_params
    
  def get_product_success_params(self, product_map):
    p_params = {}
    p_params["p_id"] = product_map["id"]
    p_params["p_vendor"] = product_map["vendor"]
    p_params["p_type"] = product_map["type"]
    p_params["p_name"] = product_map["name"]
    p_params["p_gain"] = product_map["gain"]
    return p_params
    
  def process_pixels(self):
 
    s_url = self.base_url + urllib.urlencode(self.params)
    
    s_pixel = s_url + "&event=session"
    # print "SESSION: " + s_pixel
    self.fire(s_pixel)
    #fire page view and product pixels
    
    for pv in self.session_map:
      pv_params = urllib.urlencode(self.get_pv_params(self.session_map[pv]))
      pv_url = s_url + "&" + pv_params
      pv_pixel = pv_url + "&event=pageview"
      # print "PAGEVIEW: " + pv_pixel
      self.fire(pv_pixel)
      
      for p in self.session_map[pv]["loaded"]:
        p_params = urllib.urlencode(self.get_product_opportunity_params(p))
        p_url = pv_url + "&" + p_params
        p_pixel = p_url + "&event=opportunity"
        # print "OPPORTUNITY: " + p_pixel
        self.fire(p_pixel)
        
      for p in self.session_map[pv]["succeeded"]:
        p_params = urllib.urlencode(self.get_product_success_params(p))
        p_url = pv_url + "&" + p_params
        p_pixel = p_url + "&event=success"
        # print "SUCCESS: " + p_pixel
        self.fire(p_pixel)
    
  def fire(self,pixel):
    try:
      urllib2.urlopen(pixel).read()
    except:
      pass
  
class PixelGen:
  
  def __init__(self):
    # self.delay = delay
    self.generate()
    
  def generate(self):
    while True:
      s = SessionGen()
    
p = PixelGen()
p.generate()