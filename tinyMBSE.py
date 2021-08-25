#!/usr/bin/env python
import logging
#import unittest //maybe someday
import src.cmd as mc

if __name__ == '__main__':
    # set logger info
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # create model commanding 
    model = mc.modelcmd()

    # start loop
    model.cmdloop()

