# controller
# -*- coding: utf-8 -*-
import logging



log = logging.getLogger(__name__)


class ApiWorker(object):

    def post_method(self, params):
        return params

    def get_method(self, id):
        return id




api_worker = ApiWorker()