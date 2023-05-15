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
            return jsonify({'error': 'User ID and product_id are required.'}), 400

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

        return jsonify({'success': True, 'message': f'{product_id} added to cart.'}), 200

    # 移除购物车
    def remove_cart(self, params):
        user_id = params.get('user_id')
        product_id = params.get('product_id')

        if not user_id or not product_id:
            return jsonify({'error': 'User ID and product_id are required.'}), 400

        cart_item = session.query(db.Cart).filter_by(user_id=user_id, product_id=product_id).first()

        if not cart_item:
            return jsonify({'error': 'Cart item not found.'}), 404

        session.delete(cart_item)
        session.commit()
        session.close()

        return jsonify({'success': True, 'message': f'{product_id} removed from cart.'}), 200





api_worker = ApiWorker()