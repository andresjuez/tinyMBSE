#!/usr/bin/env python
import logging
#import unittest //maybe someday
import modelcmd

if __name__ == '__main__':
    # set logger info
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # create model commanding 
    model = modelcmd.modelcmd()

    # start loop
    model.cmdloop()

