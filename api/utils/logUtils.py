import logging
import os


class Logger:
    def __init__(self, name, path, need_file=True):
        self.check_path(path)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level=logging.INFO)
        chlr = logging.StreamHandler()  # 输出到控制台的handler
        chlr.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        chlr.setFormatter(formatter)
        self.logger.addHandler(chlr)

        if need_file:
            handler = logging.FileHandler(path)
            handler.setLevel(logging.INFO)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @staticmethod
    def check_path(path):
        root_dir = path[0:path.rfind('/')]
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
