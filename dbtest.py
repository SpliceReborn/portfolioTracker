import mysql.connector
import sys
from mysql.connector import errorcode


# fees() calculate fees of trading stocks
def fees():
    # Assuming transaction value below RM10,000
    if cost < 1000.00:
        brokerage = 7.00
    else:
        brokerage = 9.00

    clearing = 0.0003 * cost
    stamp = cost // 1000 + 1.0
    serviceTax = 0.06 * brokerage

    return brokerage+clearing+stamp+serviceTax


# buy() adds fees to cost
def buy():
    totalCost = cost + fees()
    return totalCost


# average() calculates the average cost of buying the stocks (=> buy()/quantity)
def average():
    avg = round(buy(), 2)/int(quantity)

    return round(avg, 3)


# calclates wrong password attempt
count = 1
# loop to connect database, terminates program if wrong password after 3rd attempt
while True:
    try:
        password = input("Enter mysql password: ")

        connection = mysql.connector.connect(user='root',
                                             password=password,
                                             host='127.0.0.1',
                                             database='stocks_data')
        cursor = connection.cursor()
        break
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            if count == 3:
                print("Multiple failed password attempts, terminating program...")
                sys.exit()
            else:
                count += 1
                print("Wrong password")
        else:
            print(err)
    except KeyboardInterrupt:
        print()
        print("Detected keyboard interrupt, program exiting...")
        sys.exit()

while True:
    try:
        response = input("(b)uy, (s)ell, or (q)uit? ")
        if response == 'b':
            oldQuantity = 0
            ticker = input("Stock ticker? ")

            # Lines 36 - 42 checks if ticker exists in database
            query = ("SELECT ticker, quantity, average_cost FROM portfolio "
                     "WHERE ticker = %s")

            cursor.execute(query, (ticker,))
            for (ticker, quantity, average_cost) in cursor:
                oldQuantity = quantity
                oldAverage = average_cost

            # Asks price and quantity of the purchase
            price = input("What price? ")
            quantity = input("What quantity? ")

            cost = float(price) * int(quantity)
            # Calculates average cost of the purchase
            avgCost = average()

            # Executes if ticker exists, calculates real average cost and total quantity
            if oldQuantity != 0:
                previousCost = oldQuantity * float(oldAverage)
                realTotal = buy()+previousCost
                quantity = int(quantity) + oldQuantity
                realAverage = round(realTotal, 2) / quantity
                avgCost = round(realAverage, 3)

                update_stock = ("UPDATE portfolio "
                                "SET quantity = %s , average_cost = %s "
                                "WHERE ticker = %s")
                queryArguments = (quantity, avgCost, ticker)
                cursor.execute(update_stock, queryArguments)

                # Make sure data is committed to the database
                connection.commit()
            else:
                add_stock = ("INSERT INTO portfolio "
                             "(ticker, quantity, average_cost) "
                             "VALUES (%s, %s, %s)")

                queryArguments = (ticker, quantity, avgCost)

                # Insert new stock
                cursor.execute(add_stock, queryArguments)

                # Make sure data is committed to the database
                connection.commit()
        elif response == 's':
            print("This program does not support sell tracking yet")
        elif response == 'q':
            cursor.close()
            connection.close()
            sys.exit()
        else:
            print("Enter 'b', 's', or 'q' depending on what action you want to perform")
    except KeyboardInterrupt:
        cursor.close()
        connection.close()
        print()
        print("Detected keyboard interrupt, program exiting...")
        sys.exit()
