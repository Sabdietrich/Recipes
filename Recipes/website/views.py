from flask import Blueprint, render_template, request, flash, jsonify, redirect
from flask_login import login_required, current_user
from .models import Note, User
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/note', methods=['GET', 'POST'])
@login_required
def note():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home_user.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})



@views.route('/market', methods=['GET', 'POST'])
#@login_required
def market_form():
    if request.method == 'POST':
        product_names = request.form.getlist('productName')  # Retrieve list of product names
        product_prices = request.form.getlist('productPrice')  # Retrieve list of product prices

        if len(product_names) < 1:
            flash('No products added!', category='error')
        else:
            new_market = Note(product_names=','.join(product_names), product_prices=','.join(product_prices),
                            user_id=current_user.id)
            db.session.add(new_market)
            db.session.commit()
            flash('Market added!', category='success')

        return redirect('/display_info')

    return render_template('market_form.html', user=current_user)



@views.route('/display_info', methods=['GET', 'POST'])
@login_required
def display():
    markets = Note.query.filter_by(user_id=current_user.id).all()
    return render_template("display_info.html", user=current_user, markets=markets)

@views.route('/shop')
def display_info():
    users = User.query.all()
    market_data = []

    for user in users:
        market_data.append({
            'marketName': user.market_name,
            'marketPlace': user.market_place,
            'marketTime': user.market_time,
            'productNames': user.notes[0].product_names.split(',') if user.notes else [],
            'productPrices': user.notes[0].product_prices.split(',') if user.notes else []
        })

    return render_template('shop.html', market_data=market_data)


    


