import logging
import typing

import requests
import telegram
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy import Integer, BigInteger, String, Text, LargeBinary, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

import utils

if typing.TYPE_CHECKING:
    import worker

log = logging.getLogger(__name__)

# Create a base class to define all the database subclasses
TableDeclarativeBase = declarative_base()


# Define all the database tables using the sqlalchemy declarative base
class User(TableDeclarativeBase):
    """A Telegram user who used the bot at least once."""

    # Telegram data
    user_id = Column(BigInteger, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    username = Column(String)
    language = Column(String, nullable=False)

    # Current wallet credit
    credit = Column(Integer, nullable=False)

    # Extra table parameters
    __tablename__ = "users"

    def __init__(self, w: "worker.Worker", **kwargs):
        # Initialize the super
        super().__init__(**kwargs)
        # Get the data from telegram
        self.user_id = w.telegram_user.id
        self.first_name = w.telegram_user.first_name
        self.last_name = w.telegram_user.last_name
        self.username = w.telegram_user.username
        if w.telegram_user.language_code:
            self.language = w.telegram_user.language_code
        else:
            self.language = w.cfg["Language"]["default_language"]
        # The starting wallet value is 0
        # 增加超大余额，避免结算出现问题
        self.credit = 99999999

    def __str__(self):
        """Describe the user in the best way possible given the available data."""
        if self.username is not None:
            return f"@{self.username}"
        elif self.last_name is not None:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.first_name

    def identifiable_str(self):
        """Describe the user in the best way possible, ensuring a way back to the database record exists."""
        return f"user_{self.user_id} ({str(self)})"

    def mention(self):
        """Mention the user in the best way possible given the available data."""
        if self.username is not None:
            return f"@{self.username}"
        else:
            return f"[{self.first_name}](tg://user?id={self.user_id})"

    def recalculate_credit(self):
        """Recalculate the credit for this user by calculating the sum of the values of all their transactions."""
        # valid_transactions: typing.List[Transaction] = [t for t in self.transactions if not t.refunded]
        # self.credit = sum(map(lambda t: t.value, valid_transactions))
        self.credit = 99999999

    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.first_name

    def __repr__(self):
        return f"<User {self.mention()} having {self.credit} credit>"


class Product(TableDeclarativeBase):
    """A purchasable product."""

    # Product id
    id = Column(Integer, primary_key=True)
    # Product name
    name = Column(String)
    # Product description
    description = Column(Text)
    # Product price, if null product is not for sale
    price = Column(Integer)
    # Image data
    # 与ProductImage表的关系
    images = relationship("ProductImage", backref="product", lazy="dynamic")
    # Product has been deleted
    deleted = Column(Boolean, nullable=False)

    # Extra table parameters
    __tablename__ = "products"

    # No __init__ is needed, the default one is sufficient

    def text(self, w: "worker.Worker", *, style: str = "full", cart_qty: int = None):
        """Return the product details formatted with Telegram HTML. The image is omitted."""
        if style == "short":
            return f"{cart_qty}x {utils.telegram_html_escape(self.name)} - {str(w.Price(self.price) * cart_qty)}"
        elif style == "full":
            if cart_qty is not None:
                cart = w.loc.get("in_cart_format_string", quantity=cart_qty)
            else:
                cart = ''
            return w.loc.get("product_format_string", name=utils.telegram_html_escape(self.name),
                             description=utils.telegram_html_escape(self.description),
                             price=str(w.Price(self.price)),
                             cart=cart)
        else:
            raise ValueError("style is not an accepted value")

    def __repr__(self):
        return f"<Product {self.name}>"

    def send_as_message(self, w: "worker.Worker", chat_id: int) -> dict:
        """发送包含产品数据的消息。"""
        if self.images.count() > 0:
            msg = w.bot.send_photo(chat_id, self.images[0].data, caption=self.text(w))
        else:
            msg = w.bot.send_message(chat_id, self.text(w))
        return msg.to_dict()

    def set_image(self, file: telegram.File):
        """从Telegram下载图像并将其存储在product_images表中。"""
        image = ProductImage.from_file(self.id, file)
        self.images.append(image)


class ProductImage(TableDeclarativeBase):
    """与产品相关联的图像。"""

    # 产品图片id
    id = Column(Integer, primary_key=True)
    # 产品id
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    # 图像数据
    data = Column(LargeBinary)

    # 表格参数
    __tablename__ = "product_images"

    # 不需要__init__，默认的即可

    def __repr__(self):
        return f"<ProductImage {self.id}>"

    @classmethod
    def from_file(cls, product_id: int, file: telegram.File) -> "ProductImage":
        """从Telegram文件创建一个新的ProductImage实例。"""
        # 通过get请求下载照片
        r = requests.get(file.file_path)
        # 使用下载的数据创建一个新的ProductImage实例
        return cls(product_id=product_id, data=r.content)

class Cart(TableDeclarativeBase):
    '''
        购物车
    '''
    __tablename__ = 'cart'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product = relationship("Product")
    # 数量
    quantity = Column(Integer, nullable=False)
    # 总价格
    amount = Column(Float, nullable=False, default=0.0)

class Transaction(TableDeclarativeBase):
    """A TGgreed wallet transaction.
    Wallet credit ISN'T calculated from these, but they can be used to recalculate it."""

    # The internal transaction ID
    transaction_id = Column(Integer, primary_key=True)
    # The user whose credit is affected by this transaction
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    user = relationship("User", backref=backref("transactions"))
    # The value of this transaction. Can be both negative and positive.
    value = Column(Integer, nullable=False)
    # Refunded status: if True, ignore the value of this transaction when recalculating
    refunded = Column(Boolean, default=False)
    # Extra notes on the transaction
    notes = Column(Text)

    # Payment provider
    provider = Column(String)
    # Transaction ID supplied by Telegram
    telegram_charge_id = Column(String)
    # Transaction ID supplied by the payment provider
    provider_charge_id = Column(String)
    # Extra transaction data, may be required by the payment provider in case of a dispute
    payment_name = Column(String)
    payment_phone = Column(String)
    payment_email = Column(String)

    # Order ID
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    order = relationship("Order", back_populates="transaction")

    # Extra table parameters
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("provider", "provider_charge_id"),)

    def text(self, w: "worker.Worker"):
        string = f"<b>T{self.transaction_id}</b> | {str(self.user)} | {w.Price(self.value)}"
        if self.refunded:
            string += f" | {w.loc.get('emoji_refunded')}"
        if self.provider:
            string += f" | {self.provider}"
        if self.notes:
            string += f" | {self.notes}"
        if self.payment_name:
            string += f" | {self.payment_name}"
        if self.payment_phone:
            string += f" | +{self.payment_phone}"
        if self.payment_email:
            string += f" | {self.payment_email}"
        return string

    def __repr__(self):
        return f"<Transaction {self.transaction_id} for User {self.user_id}>"


class Admin(TableDeclarativeBase):
    """A TGgreed administrator with his permissions."""

    # The telegram id
    user_id = Column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    user = relationship("User")
    # Permissions
    edit_products = Column(Boolean, default=False)
    receive_orders = Column(Boolean, default=False)
    create_transactions = Column(Boolean, default=False)
    display_on_help = Column(Boolean, default=False)
    is_owner = Column(Boolean, default=False)
    # Live mode enabled
    live_mode = Column(Boolean, default=False)

    # Extra table parameters
    __tablename__ = "admins"

    def __repr__(self):
        return f"<Admin {self.user_id}>"


class Order(TableDeclarativeBase):
    """An order which has been placed by an user.
    It may include multiple products, available in the OrderItem table."""

    # The unique order id
    order_id = Column(Integer, primary_key=True)
    # The user who placed the order
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    user = relationship("User", lazy='joined')
    # Date of creation
    creation_date = Column(DateTime, nullable=False)
    # Date of delivery
    delivery_date = Column(DateTime)
    # Date of refund: if null, product hasn't been refunded
    refund_date = Column(DateTime)
    # Refund reason: if null, product hasn't been refunded
    refund_reason = Column(Text)
    # List of items in the order
    items: typing.List["OrderItem"] = relationship("OrderItem", back_populates="order", lazy='joined')
    # Extra details specified by the purchasing user
    notes = Column(Text)
    # Linked transaction
    transaction = relationship("Transaction", back_populates="order", uselist=False, lazy='joined')
    # tracking_number
    tracking_number = Column(String)
    # quantity
    quantity = Column(Integer, nullable=False, default=1)

    # Extra table parameters
    __tablename__ = "orders"

    def __repr__(self):
        return f"<Order {self.order_id} placed by User {self.user_id}>"

    def text(self, w: "worker.Worker", user=False):
        items = ""
        for item in self.items:
            items += item.text(w) + "\n"
        if self.delivery_date is not None:
            status_emoji = w.loc.get("emoji_completed")
            status_text = w.loc.get("text_completed")
        elif self.refund_date is not None:
            status_emoji = w.loc.get("emoji_refunded")
            status_text = w.loc.get("text_refunded")
        else:
            status_emoji = w.loc.get("emoji_not_processed")
            status_text = w.loc.get("text_not_processed")
        if user and w.cfg["Appearance"]["full_order_info"] == "no":
            return w.loc.get("user_order_format_string",
                             status_emoji=status_emoji,
                             status_text=status_text,
                             items=items,
                             notes=self.notes,
                             value=str(w.Price(-self.transaction.value))) + \
                   (w.loc.get("refund_reason", reason=self.refund_reason) if self.refund_date is not None else "")
        else:
            return status_emoji + " " + \
                   w.loc.get("order_number", id=self.order_id) + "\n" + \
                   w.loc.get("order_format_string",
                             user=self.user.mention(),
                             date=self.creation_date.isoformat(),
                             items=items,
                             notes=self.notes if self.notes is not None else "",
                             value=str(w.Price(-self.transaction.value))) + \
                   (w.loc.get("refund_reason", reason=self.refund_reason) if self.refund_date is not None else "")


class OrderItem(TableDeclarativeBase):
    """A product that has been purchased as part of an order."""

    # The unique item id
    item_id = Column(Integer, primary_key=True)
    # The product that is being ordered
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product = relationship("Product", lazy='joined')
    # The order in which this item is being purchased
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    order = relationship("Order", back_populates="items", lazy='joined')

    # Extra table parameters
    __tablename__ = "orderitems"

    def text(self, w: "worker.Worker"):
        return f"{self.product.name} - {str(w.Price(self.product.price))} \n快递单号：{self.order.tracking_number if self.order.tracking_number else '暂无'}\n"

    def __repr__(self):
        return f"<OrderItem {self.item_id}>"
