from scrapy import cmdline


cmdline.execute("scrapy crawl Magnit -o dump.json".split())
