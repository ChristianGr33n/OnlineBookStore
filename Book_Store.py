import psycopg2

#connects this file to the postgresql database
#note: "user=postgres" and/or "password=postgres" may have to be changed to work on your postgresql
def connect_to_db():
    try:
        connection = psycopg2.connect("dbname=BookStore user=postgres password=Cookie678")  #<-- modify these values if needed
    except:
        print("Could not connect to database")
    return connection

#returns the book with the given book id (bid) and store number (snum)
def get_book(bid):
    if(not bid.isnumeric()):
        return -1
    con = connect_to_db()
    cur = con.cursor()
    book_query = 'SELECT * FROM book WHERE bid = %s'
    cur.execute(book_query, (bid,))
    return cur.fetchone()

#returns the store book with the given book id (bid) and store number (snum)
def get_store_book(bid, snum):
    if(not bid.isnumeric() or not snum.isnumeric()):
        return -1
    con = connect_to_db()
    cur = con.cursor()
    book_query = 'SELECT * FROM store_book WHERE bid = %s AND snum = %s'
    cur.execute(book_query, (bid, snum,))
    return cur.fetchone()

#prints out the results of a book search
def print_search(cur, store_books):
    ##showing the Customer the top 8 results (or less if there isn't 8)
    resultsLength = 8
    if(len(store_books)<8):
        resultsLength = len(store_books)
    for i in range(resultsLength):
        print(str(i+1) + ".  Book: " + store_books[i][5] +", pages: " + str(store_books[i][3]) + ", price: " + str(store_books[i][1]) + ", publisher: " + store_books[i][4], end='')
        cur.execute( "SELECT genre FROM genre WHERE bid = %s", (store_books[i][0],))
        print(", genres: ", cur.fetchall(), end='')
        cur.execute( "SELECT author FROM author WHERE bid = %s", (store_books[i][0],))
        print(", authors: ", cur.fetchall())
    return resultsLength

#all in one search where the Customer can search for anything in any of columns: name, author, genre
def book_search(cart, snum):
    con = connect_to_db()
    cur = con.cursor()
    answer = input("Search: ")

    ##doing queries on book names, authors, genres to fetch any matches 
    name_query = "SELECT s.bid FROM store_book s, book b WHERE s.bid = b.bid AND b.name = %s AND s.quantity > 0"
    cur.execute(name_query, (answer,))
    books = cur.fetchall()
    author_query = "SELECT s.bid FROM author a, store_book s, book b WHERE a.author = %s AND a.bid = b.bid AND b.bid = s.bid AND s.quantity > 0"
    cur.execute(author_query, (answer,))
    books += cur.fetchall()
    genre_query = "SELECT s.bid FROM genre g, store_book s, book b WHERE g.genre = %s AND g.bid = b.bid AND b.bid = s.bid AND s.quantity > 0"
    cur.execute(genre_query, (answer,))
    books += cur.fetchall()

    ##doing a query to grab all of the books in the array that are also in the store.
    ##store_book_query = "SELECT * FROM store_book WHERE bid = ANY (%s)"
    store_book_query = "SELECT * FROM book WHERE bid = ANY(SELECT bid FROM store_book WHERE bid = ANY (%s))"
    cur.execute(store_book_query, (books,))
    store_books = cur.fetchall()
    resultsLength = print_search(cur, store_books)

    add_to_cart=''
    while(add_to_cart != 'back'):
        add_to_cart = input('\nEnter Book position to add to cart. (back) to go back: ')
        if(add_to_cart == 'back'):
            return
        elif (add_to_cart.isnumeric() and int(add_to_cart) <= resultsLength and int(add_to_cart) > 0):
            #add the book to the cart
            cart.append(store_books[int(add_to_cart)-1])
            print(cart)

#turns a user's cart into an order and makes appropriate changes to the quantity of books from the store
def checkout(cart, snum):
    con = connect_to_db()
    cur = con.cursor()
    ##checks if the cart is empty
    if(len(cart)==0):
        print("There is nothing in your cart")
        return

    ##checks if the customer is registered
    email = input("please enter your email login to complete checkout: ")
    registration_query = "SELECT * FROM Customer WHERE email = %s"
    cur.execute(registration_query, (email,))
    customer = cur.fetchone()
    if(customer==None):
        print("Please register your account in the menu to checkout")
        return
    shipping = input("Enter shipping address: ")
    billing = input("Enter billing address: ")

    ##adding the order and sale for each book to the database
    while(len(cart) != 0):
        order = cart[0]
        quantity = cart.count(order)
        #checking that the store has this quantity
        book_query = "SELECT quantity FROM store_book WHERE snum = %s AND bid = %s"
        cur.execute(book_query, (snum, cart[0][0]))
        store_quantity = cur.fetchone()[0]

        #if the store has more or equal the amount of books the customer is buying, finalize checkout
        if(quantity <= store_quantity):
            #INSERTING the order into bk_order
            order_query = "INSERT INTO bk_order (shipping, billing, uid, bid, quantity) VALUES(%s, %s, %s, %s, %s) RETURNING onum"
            cur.execute(order_query, (shipping, billing, customer[3], cart[0][0], quantity))
            onum = cur.fetchone()[0]
            #INSERTING the sale into sale
            sale_query = "INSERT INTO sale (bid, quantity, snum) VALUES(%s, %s, %s)"
            cur.execute(sale_query, (cart[0][0], quantity, snum))
            ##substracting the quantity
            modify_quantity_query = 'UPDATE store_book SET quantity = %s WHERE snum = %s AND bid = %s'
            cur.execute(modify_quantity_query, ((store_quantity - quantity), snum, cart[0][0],))
            print("your order number is: ", onum, "   for ", cart[0][5])
            con.commit()
            if ((store_quantity - quantity) == 0):
                print("*sending email to publisher for more copies of ", cart[0][5], "*")
        else:
            print("The store does not have enough copies of ", cart[0][5], " to meet your demand (Store has ", store_quantity, ")" )
        ##deleting all of the same books that we ordered from the list
        for i in range(quantity):
            cart.remove(order)



#prompts the user to add them and their info into the User table
def register():
    con = connect_to_db()
    cur = con.cursor()

    fName = input("First name: ")
    lName = input("Last name: ")
    email = input("Email: ")
    registration_query = "INSERT INTO Customer (fname, lname, email) VALUES(%s, %s, %s)"
    cur.execute(registration_query, (fName, lName, email))
    con.commit()

#promts user to track an order given the order number (onum) and prints details about the order
def track_order():
    onum=''
    while(onum!='back'):
        onum = input("\nEnter an order number (back) to go back: ")
        ##sanitization
        
        if(onum.isnumeric() == False):
            continue
        #look for the order in the database
        con = connect_to_db()
        cur = con.cursor()
        registration_query = "SELECT * FROM bk_order WHERE onum = %s"
        cur.execute(registration_query, (int(onum),))
        order = cur.fetchone()
        print(order)
        if(order != None):
            book = get_book(str(order[4]))
            print("ORDER DETAILS\norder number: ".ljust(15), onum, "\nbook: ".ljust(15), book[5], "\nshipping to: ".ljust(15), order[1], "\nquantity: ".ljust(15), order[5] )
            print("order in transit...")
        else:
            print("no such order")

#prompts user to add a new book to a store's collection
def add_new_book():
    con = connect_to_db()
    cur = con.cursor()
    book_id = input("Enter the book id (bid) that you would like to add: ")
    snum = input("Enter store number (snum) to ship to: ")
    ##checking if its already in the book store collection
    store_book = get_store_book(book_id, snum)
    if(store_book == -1):
        print("invalid bid")
        return
    elif(store_book != None):
        print("Book with id %s is already in this store collection", book_id)
        return 
    ##checking that its a book in the book table
    book = get_book(book_id)
    if(book == -1):
        print("invalid bid")
        return
    elif(book == None):
        print("no such book exists in the book table (must exist in the book table to be added to the store_book table")
        return
    elif(book != None):
        quantity = input("Enter quantity: ")
        ##checking if store with snum exists
        store_query = 'SELECT * FROM store WHERE snum = %s'
        cur.execute(store_query, (snum,))
        if(cur.fetchone() == None):
            print("no such store with snum")
            return
        
        #add the book to the store
        insert_book_query = "INSERT INTO store_book (bid, quantity, restock, snum) VALUES(%s, %s, %s, %s)"
        cur.execute(insert_book_query, (book_id, quantity, quantity, snum,))  #default restock value will be set to the initial quantity (as per the requirements)
        con.commit()

#prompts user to remove a book from a store's collection given the book's id (bid) and removes it
def remove_book():
    con = connect_to_db()
    cur = con.cursor()

    book_id = input("Enter the book id (bid) that you would like to remove: ")
    snum = input("Enter store number (snum) to remove the book from: ")

    ##checking if store exists
    store_query = 'SELECT * FROM store WHERE snum = %s'
    cur.execute(store_query, (snum,))
    if(cur.fetchone() == None):
        print("no such store with snum")
        return

    ##chcking if book exists in store
    store_book = get_store_book(book_id, snum)
    if(store_book == -1):
        print("invalid bid")
        return
    elif(store_book == None):
        print("no such book with bid %s in the collection")
    elif(store_book != None):
        #remove the book
        remove_book_query = "DELETE FROM store_book WHERE bid = %s AND snum = %s"
        cur.execute(remove_book_query, (book_id, snum,))  
        con.commit()
        
#reports the number of sales, revenue, expenses, and profit for the store that is logged into
def get_sales_expense(snum):
    con = connect_to_db()
    cur = con.cursor()
    expense = 0
    revenue = 0
    num_sales = 0
    print("\nSALES VS EXPENSES REPORT\n-----------------------------")
    ##go into sales and calculate (price - price*percentage)*quantity for each book in sales
    #getting a list of books that were sold from this store
    sale_query = 'SELECT * FROM sale WHERE snum = %s'
    cur.execute(sale_query, (snum,))
    sales = cur.fetchall()
    #iterate through each sale and calculate the sale and expense
    for sale in sales:
        quantity = sale[2]
        bid = sale[1]
        book_query = 'SELECT price, percentage FROM book WHERE bid = %s'
        cur.execute(book_query, (bid,))
        book = cur.fetchall()[0]
        price = book[0]
        percentage = book[1]
        revenue += price*quantity
        expense += (price*percentage)*quantity
        num_sales += quantity
    print("# of Sales       Revenue      Expense     Profit")
    print(str(num_sales).ljust(16), str(revenue).ljust(12), str(expense).ljust(11), str(revenue-expense).ljust(15))

# shows the revenue made in sales for each author in a given store
# Since a book can have multiple authors, the authors revenue does not add up to the stores revenue
# ex: if a sold book was $10 and had authors JK and Rowling, both of those authors would be incremented by 10
def get_sales_per_author(snum):
    con = connect_to_db()
    cur = con.cursor()
    sale_query = 'SELECT s.quantity, a.author, b.price FROM Sale s, Author a, book b WHERE s.snum = %s AND s.bid = b.bid AND b.bid = a.bid'
    cur.execute(sale_query, (snum,))
    sales = cur.fetchall()
    author_query = 'SELECT DISTINCT a.author FROM  Sale s, Author a WHERE s.snum = %s AND s.bid = a.bid'
    cur.execute(author_query, (snum,))
    temp_authors = cur.fetchall()

    authors = []
    #cleaning up the genres array
    for author in temp_authors:
        authors.append(author[0])
    sale_per_author = [0]*len(authors)
    # adding the revenue for each sale and adding it to the corresponding genre
    for sale in sales:
        index = authors.index(sale[1])
        sale_per_author[index] += sale[0]*sale[2]
    for i in range(len(authors)):
        print((authors[i] + ":   ").ljust(20), sale_per_author[i] )

# shows the revenue made in sales for each genre in a given store
# Since a book can have multiple genres, the genres revenue does not add up to the stores revenue
# ex: if a sold book was $10 and was under fantasy and adventure, both of those genres would be incremented by 10
def get_sales_per_genre(snum):
    con = connect_to_db()
    cur = con.cursor()
    sale_query = 'SELECT s.quantity, g.genre, b.price FROM Sale s, Genre g, book b WHERE s.snum = %s AND s.bid = b.bid AND b.bid = g.bid'
    cur.execute(sale_query, (snum,))
    sales = cur.fetchall()
    genre_query = 'SELECT DISTINCT g.genre FROM  Sale s, Genre g WHERE s.snum = %s AND s.bid = g.bid'
    cur.execute(genre_query, (snum,))
    temp_genres = cur.fetchall()

    genres = []
    #cleaning up the genres array
    for genre in temp_genres:
        genres.append(genre[0])
    sale_per_genre = [0]*len(genres)
    # adding the revenue for each sale and adding it to the corresponding genre
    for sale in sales:
        index = genres.index(sale[1])
        sale_per_genre[index] += sale[0]*sale[2]
    for i in range(len(genres)):
        print((genres[i] + ":   ").ljust(20), sale_per_genre[i] )

    

#Shows a report to the user based on the store number (snum) that was given as input.
#A small menu of report options are given to the user.
#to access a report, user must input the corresponding number from the list/menu.
def report(snum):
    answer=''
    while(answer != 'back' and answer != '4'):
        answer = input("\nREPORTS\n1. Sales vs. Expense\n2. Sales per Author\n3. Sales per Genre\n4. back\n>")
        if(answer=='1'):
            get_sales_expense(snum)
        elif(answer=='2'):
            get_sales_per_author(snum)
        elif(answer=='3'):
            get_sales_per_genre(snum)

#logs into the store with the given store number (snum)
def login(cur):
    store = None
    snum = '-1'
    while(store == None):
        snum = input("please choose a store id (snum) to enter (exit) to quit: ")
        if(snum == 'exit'):
            return 'exit'
        if(not snum.isnumeric()):
            break
    
        store_query = 'SELECT * FROM store WHERE snum = %s'
        cur.execute(store_query, (snum,))
        store = cur.fetchone()

        if(store == None):
            print("no such store with snum (try '1')")
            continue
    return snum


def main():
    con = connect_to_db()
    cur = con.cursor()
    ##menu
    print("Welcome the to BookStore!\n")
    snum=''
    while(snum!="exit"):
        snum = login(cur)
        if(not snum.isnumeric()):
            continue
        answer=''
        while(answer!='back'):
            answer = input("Are you a customer (c) or an owner (o)? (back) to return. (reg) to register: ")
            if(answer=='c'):
                ##the customer's cart is not stored in the DB since it is a temporary array. (no point in holding it in the db when it will be earased quickly)
                ##it is reset after an order or leaving the customer UI.
                cart=[]

                print("\n\n----------------------------------------------------")
                print("Welcome Customer. Please choose an option below")
                while(answer != '4' and answer!='back'):
                    answer = input("1. Search for a book\n2. Track an order\n3. Checkout\n4. back\n>")
                    if(answer=='1'):
                        book_search(cart, snum) 
                    elif(answer=='2'):
                        track_order()
                    elif(answer=='3'):
                        checkout(cart, snum)
                answer='' #resets user input
            elif(answer=='o'):
                print("\n\n----------------------------------------------------")
                print("Welcome Owner. Please choose an option below")
                while(answer!='4' and answer!='back'):
                    answer = input("1. Add new book\n2. Remove book\n3. View reports\n4. back\n>")
                    if(answer=='1'):
                        add_new_book()
                    elif(answer=='2'):
                        remove_book()
                    elif(answer=='3'):
                        report(snum)
                answer='' #resets user input
            elif(answer=='reg'):
                register()
                answer='' #resets user input


            print("\n")

if __name__ == "__main__":
    main()