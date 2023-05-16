# controller
# -*- coding: utf-8 -*-
import logging
from flask import jsonify, make_response
import os
import logging
import queue as queuem
import requests
import sqlalchemy
import database as db




log = logging.getLogger(__name__)

# init session
db_engine = os.environ.get("DB_ENGINE")
engine = sqlalchemy.create_engine(db_engine)
session = sqlalchemy.orm.sessionmaker(bind=engine)()


class ApiWorker(object):

    # 直接加入购物车
    def add_cart(self, params):
        user_id = params.get('user_id')
        product_id = params.get('product_id')
        quantity = params.get('quantity')

        if not user_id or not product_id:
            return {'error': 'User ID and product_id are required.'}

        cart_item = session.query(db.Cart).filter_by(user_id=user_id, product_id=product_id).first()
        per_price = session.query(db.Product).filter_by(id=product_id).first().price

        if not cart_item:
            # amount equals price * quantity
            amount = per_price * quantity
            cart_item = db.Cart(user_id=user_id, product_id=product_id, quantity=quantity, amount=amount)
            session.add(cart_item)
        else:
            amount = per_price * quantity
            cart_item.quantity = quantity
            cart_item.amount = amount

        session.commit()
        session.close()

        return {'success': True, 'message': f'{product_id} added to cart.'}

    # 移除购物车
    def remove_cart(self, params):
        user_id = params.get('user_id')
        product_id = params.get('product_id')

        if not user_id or not product_id:
            return {'error': 'User ID and product_id are required.'}

        cart_item = session.query(db.Cart).filter_by(user_id=user_id, product_id=product_id).first()

        if not cart_item:
            return {'error': 'Cart item not found.'}

        session.delete(cart_item)
        session.commit()
        session.close()

        return {'success': True, 'message': f'{product_id} removed from cart.'}


    # 购物车列表
    def cart_list(self, params):
        user_id = params.get('user_id')

        if not user_id:
            return {'error': 'User ID is required.'}

        cart_items = session.query(db.Cart).filter_by(user_id=user_id).all()

        if not cart_items:
            return {'error': 'Cart is empty.'}

        cart_list = []
        for item in cart_items:
            # add product info
            product = session.query(db.Product).filter_by(id=item.product_id).first()
            item.product_name = product.name
            item.product_price = product.price
            item.product_image = product.image
            cart_list.append(item)

        session.close()

        return {'success': True, 'cart_list': cart_list}



api_worker = ApiWorker()