from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import Users, Items
from cloudipsp import Api, Checkout
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def index():
    items = Items.query.all()
    return render_template('index.html', data=items)


@main.route('/mylots')
@login_required
def mylots():
    items = Items.query.filter(Items.user_id == current_user.get_id()).all()
    return render_template('mylots.html', data=items)


@main.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        time = request.form['time']

        item = Items(title=title, price=price, time=time, user=current_user)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect(url_for('main.index'))
        except:
            return "При создании лота произошла ошибка"
    else:
        return render_template('create.html')


@main.route('/buy/<int:id>')
@login_required
def item_buy(id):
    item = Items.query.get(id)

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "RUB",
        "amount": str(item.price * 3) + "00"
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@main.route('/bet/<int:id>', methods=['POST', 'GET'])
@login_required
def item_change_price(id):
    item = Items.query.get(id)
    if request.method == "POST":
        item.price = request.form['price']

        try:
            db.session.commit()
            return redirect(url_for('main.index'))
        except:
            return "При изменении ставки произошла ошибка"
    else:
        return render_template('bet.html', item=item)


@main.route('/info/<int:id>')
def item_info(id):
    item = Items.query.get(id)
    dt = item.time
    year = dt[0:4]
    month = dt[5:7]
    day = dt[8:10]
    hour = dt[11:13].replace('00', '0')
    min = dt[14:16].replace('00', '0')
    lotdt = datetime(int(year), int(month), int(day), int(hour), int(min))
    now = datetime.now()
    diff = lotdt - now
    a = str(diff)
    if a[0] == '-':
        return render_template('info2.html')
    else:
        return render_template('info.html', diff=diff)


@main.route('/changemylot/<int:id>', methods=['POST', 'GET'])
@login_required
def changemylot(id):
    item = Items.query.get(id)
    if request.method == "POST":
        item.title = request.form['title']
        item.price = request.form['price']
        item.time = request.form['time']

        try:
            db.session.commit()
            return redirect(url_for('main.index'))
        except:
            return "При изменении лота произошла ошибка"
    else:
        return render_template('change.html', item=item)


@main.route('/delete/<int:id>')
@login_required
def delete(id):
    item = Items.query.get_or_404(id)

    try:
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for('main.mylots'))
    except:
        return "При удалении произошла ошибка"
