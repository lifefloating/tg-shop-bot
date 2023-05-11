import logging
import os
import sys
from logging.handlers import SysLogHandler
from logging.handlers import TimedRotatingFileHandler

level = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR
}


class LogFileHandler(TimedRotatingFileHandler):
    
    def __init__(self, *args, **kwargs):
        TimedRotatingFileHandler.__init__(self, *args, **kwargs)
        os.dup2(self.stream.fileno(), sys.stderr.fileno())

    def doRollover(self):
        TimedRotatingFileHandler.doRollover(self)
        os.dup2(self.stream.fileno(), sys.stderr.fileno())



def init(
    daemon=False, logger_file='', name_dict={}, module_dict={}, module_name='',
    handler_class=LogFileHandler
):
    """
    The common logger helper

    :param daemon: True: logging to file, False: logging to console
    :param logger_file: File path, required when dameon=True
    :param name_dict: name level dict, eg: {'app': logging.INFO}
    :param module_dict: module level dict, egg: {app.logger: logging.INFO}
    :param module_name: name of module, eg: 'OPENSTACK-AGENT'
    :param handler_class: object of class of logging.handler
    """
    if daemon:
        log_handler = handler_class(
            logger_file, when='midnight', backupCount=365
        )
    else:
        log_handler = logging.StreamHandler()

    log_formatter = logging.Formatter(
        '%(asctime)s T%(thread)d-%(threadName)s '
        '%(levelname)s %(module)s.'
        '%(funcName)s.%(lineno)s: %(message)s'
    )
    log_handler.setFormatter(log_formatter)

    if module_name:
        syslog_handler = SysLogHandler(
            address='/usr/local/services/log', facility=SysLogHandler.LOG_LOCAL3
        )
        syslog_formatter = logging.Formatter(module_name + '/%(module)s: %(message)s')
        syslog_handler.setFormatter(syslog_formatter)
        syslog_filter = logging.Filter()
        syslog_filter.filter = lambda record: \
            record.levelno == logging.WARNING or \
            record.levelno == logging.ERROR
        syslog_handler.addFilter(syslog_filter)

    _default_name_level = {
        __name__: logging.DEBUG,
        "__main__": logging.DEBUG,
    }
    _name_dict = dict()
    _name_dict.update(_default_name_level)
    _name_dict.update(name_dict)

    for name, level in _name_dict.items():
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(log_handler)
        if module_name:
            logger.addHandler(syslog_handler)
    for module_logger, level in module_dict.items():
        module_logger.setLevel(level)
        module_logger.addHandler(log_handler)
        if module_name:
            logger.addHandler(syslog_handler)
