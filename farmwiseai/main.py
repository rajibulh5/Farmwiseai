from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from sqlalchemy.orm import class_mapper

def serialize(model):
    """Serialize a SQLAlchemy model to a dictionary."""
    columns = [column.key for column in class_mapper(model.__class__).columns]
    return {column: getattr(model, column) for column in columns}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)

basic_auth = BasicAuth(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()



# Set up basic authentication
app.config['BASIC_AUTH_USERNAME'] = 'farmwiseai'
app.config['BASIC_AUTH_PASSWORD'] = 'ai'

# Enforce authentication for all routes
basic_auth.init_app(app)


@app.route('/')
def home():
    return "welcome"
# Endpoint to add a new book
@app.route('/books', methods=['POST'])
@basic_auth.required
def add_book():
    data = request.get_json()
    new_book = Book(**data)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully"}), 201

# Endpoint to retrieve all books
@app.route('/books')
def get_all_books():
    books = Book.query.all()
    book_list = []

    for book in books:
        book_data = {
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "price": book.price,
            "quantity": book.quantity
        }
        book_list.append(book_data)

    return jsonify(book_list)

# Endpoint to retrieve a specific book by ISBN
@app.route('/books/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        return jsonify(serialize(book))
    return jsonify({"message": "Book not found"}), 404

# Endpoint to update book details
@app.route('/books/<isbn>', methods=['PUT'])
@basic_auth.required
def update_book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    
    if book:
        data = request.get_json()
        
        # Update only the fields provided in the request
        for key, value in data.items():
            setattr(book, key, value)
        
        db.session.commit()
        
        return jsonify({"message": "Book updated successfully"})
    
    return jsonify({"message": "Book not found"}), 404

# Endpoint to delete a book
@app.route('/books/<isbn>', methods=['DELETE'])
@basic_auth.required
def delete_book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted successfully"})
    return jsonify({"message": "Book not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
