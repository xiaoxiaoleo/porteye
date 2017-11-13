# -*- coding:utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)5s %(filename)15s[%(lineno)03d] %(funcName)20s(): %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')


def set_log_file_name(file_name):
    #################################################################################################
    # 定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大10M
    Rthandler = RotatingFileHandler(file_name, maxBytes=10 * 1024 * 1024, backupCount=5)
    Rthandler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(name)-12s: %(asctime)s %(levelname)5s %(filename)15s[%(lineno)03d] %(funcName)20s(): %(message)s')
    Rthandler.setFormatter(formatter)
    ################################################################################################

    logging.getLogger("").addHandler(Rthandler)
