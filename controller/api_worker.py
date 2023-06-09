# controller
# -*- coding: utf-8 -*-
import logging
from flask import jsonify, make_response
import os
import logging
import queue as queuem
import requests
import sqlalchemy
from sqlalchemy.orm import joinedload
import database as db
import base64
import datetime




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
        product_id = int(product_id)
        quantity = params.get('quantity')

        if not user_id or not product_id:
            raise ValueError('User ID and product_id are required.')

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
        product_id = int(product_id)

        if not user_id or not product_id:
            raise ValueError('User ID and product_id are required.')

        cart_item = session.query(db.Cart).filter_by(user_id=user_id, product_id=product_id).first()

        if not cart_item:
            raise ValueError('Cart item not found.')

        session.delete(cart_item)
        session.commit()
        session.close()

        return {'success': True, 'message': f'{product_id} removed from cart.'}


    # 购物车列表
    def cart_list(self, params):
        user_id = params.get('user_id')

        if not user_id:
            # 网页端进来正常没user_id 兼容下 不然进来就报错
            return {'success': True, 'cart_list': []}
            # raise ValueError('User ID is required.')

        cart_items = session.query(db.Cart).options(joinedload(db.Cart.product)).filter_by(user_id=user_id).all()

        if not cart_items:
            return {'success': True, 'cart_list': []}

        cart_list = []
        for item in cart_items:
            # add product info
            cart_list.append({
                'product_id': item.product_id,
                'product_name': item.product.name,
                'product_price': item.product.price,
                'product_description': item.product.description,
                'product_image':  base64.b64encode(item.product.images[0].data).decode('utf-8'),
                'quantity': item.quantity,
                'amount': item.amount
            })

        session.close()

        return {'success': True, 'cart_list': cart_list}


    # 订单列表
    def order_list(self, params):
        user_id = params.get('user_id')

        if not user_id:
            raise ValueError('User ID is required.')

        orders = session.query(db.Order).filter_by(user_id=user_id).all()

        if not orders:
            raise ValueError('No order found.')

        order_list = []
        for order in orders:
            order_list.append({
                'order_id': order.order_id,
                'order_date': order.creation_date,
                'order_delivery_date': order.delivery_date,
                'order_notes': order.notes or '',
                'order_tracking_number': order.tracking_number or '',
            })

        session.close()

        return {'success': True, 'order_list': order_list}

    # 商品列表
    def product_list(self):
        products = session.query(db.Product.id, db.Product.name, db.Product.price, db.Product.description, db.ProductImage.data)\
                        .outerjoin(db.ProductImage, db.Product.id == db.ProductImage.product_id)\
                        .all()

        if not products:
            return {'success': True, 'product_list': []}

        product_list = []
        for product in products:
            found = False
            for item in product_list:
                if item['product_id'] == product.id:
                    item['product_image'].append(base64.b64encode(product.data).decode('utf-8'))
                    found = True
                    break

            if not found:
                product_list.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_price': product.price,
                    'product_description': product.description,
                    'product_image': [base64.b64encode(product.data).decode('utf-8')] if product.data is not None else []
                })

        session.close()

        return {'success': True, 'product_list': product_list}
    
    # 搜索商品
    def search_products(self, params):
        keyword = params.get('keyword')
        products = session.query(db.Product.id, db.Product.name, db.Product.price, db.Product.description, db.ProductImage.data)\
                        .outerjoin(db.ProductImage, db.Product.id == db.ProductImage.product_id)\
                        .filter(db.Product.name.ilike(f"%{keyword}%"))\
                        .all()

        if not products:
            return {'success': True, 'product_list': []}

        product_list = []
        for product in products:
            found = False
            for item in product_list:
                if item['product_id'] == product.id:
                    item['product_image'].append(base64.b64encode(product.data).decode('utf-8'))
                    found = True
                    break

            if not found:
                product_list.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_price': product.price,
                    'product_description': product.description,
                    'product_image': [base64.b64encode(product.data).decode('utf-8')] if product.data is not None else []
                })

        session.close()

        return {'success': True, 'product_list': product_list}


     # 商品详情
    def product_detail(self, params):
        product_id = params.get('product_id')
        product_id = int(product_id)
        # 查询有问题，改成内存筛选
        products = session.query(db.Product.id, db.Product.name, db.Product.price, db.Product.description, db.ProductImage.data)\
                        .outerjoin(db.ProductImage, db.Product.id == db.ProductImage.product_id)\
                        .all()
        
        products = [product for product in products if product.id == product_id]

        if not products:
            raise ValueError('product not found')

        product_list = []
        for product in products:
            found = False
            for item in product_list:
                if item['product_id'] == product.id:
                    item['product_image'].append(base64.b64encode(product.data).decode('utf-8'))
                    found = True
                    break

            if not found:
                product_list.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_price': product.price,
                    'product_description': product.description,
                    'product_image': [base64.b64encode(product.data).decode('utf-8')] if product.data is not None else []
                })

        if not product_list:
            raise ValueError('product not found')

        result = product_list[0]

        session.close()

        return {'success': True, 'product': result}


    
    # 根据传来的product_id quantity user_id 创建订单 
    def create_order(self, params):
        with session as sess:
            user_id = params.get('user_id')
            product_id = params.get('product_id')
            product_id = int(product_id)
            quantity = params.get('quantity')
            notes = params.get('notes')
            if not notes:
                raise ValueError('请填写备注，并且填写收货信息')
            if not user_id or not product_id:
                raise ValueError('User ID and product_id are required.')
            # 生成订单
            order = db.Order(user_id=user_id, notes=notes, tracking_number='', creation_date=datetime.datetime.now(), quantity=quantity)
            sess.add(order)
            sess.commit()
            # 查询product
            product = sess.query(db.Product).filter_by(id=product_id).one()
            # 生成订单详情
            order_detail = db.OrderItem(order=order, product=product)
            sess.add(order_detail)
            sess.commit()

            # 查询新插入的订单
            newOrder = sess.query(db.Order).filter_by(order_id=order.order_id).one()     

        return {'success': True, 'order': newOrder}


api_worker = ApiWorker()