import psycopg2

# MERK: Må kjøres med Python 3

user = 'martgul' # Sett inn ditt UiO-brukernavn ("_priv" blir lagt til under)
pwd = 'so8UZoop4E' # Sett inn passordet for _priv-brukeren du fikk i en mail

connection = \
    "dbname='" + user + "' " +  \
    "user='" + user + "_priv' " + \
    "port='5432' " +  \
    "host='dbpg-ifi-kurs.uio.no' " + \
    "password='" + pwd + "'"

def administrator():
    conn = psycopg2.connect(connection)

    ch = 0
    while (ch != 3):
        print("-- ADMINISTRATOR --")
        print("Please choose an option:\n 1. Create bills\n 2. Insert new product\n 3. Exit")
        ch = int(input("Option: \n >>"))

        if (ch == 1):
            make_bills(conn)
        elif (ch == 2):
            insert_product(conn)

def make_bills(conn):
    peker = conn.cursor()
    print('\n')
    print('--BILLS--')

    bruker = input('Username: \n >>')

    q ="\
        WITH pris AS (\
            SELECT p.pid, o.uid, p.price * o.num AS price\
                FROM ws.products AS p\
                INNER JOIN ws.orders AS o\
                    USING (pid)\
            WHERE o.payed = 0\
        ),\
        ubetalt AS (\
            SELECT o.uid, sum(o.price) AS ubetalt\
                FROM pris AS o\
                GROUP BY o.uid\
        )\
            SELECT u.name, u.address, t.ubetalt\
                FROM ws.users AS u\
                    INNER JOIN ubetalt AS t\
                        USING (uid)"

    if bruker == "":
        peker.execute(q + ";")
    else:
        peker.execute(q + " WHERE u.username = %(bruker)s;", {'bruker': bruker})

    rader = peker.fetchall()
    if len(rader) == 0:
        print("User %s not found ...\n" % (bruker))
    else:
        print()
        for rad in rader:
            print("-- BILL --")
            print("Name: %s" % (rad[0]))
            print("Address: %s" % (rad[1]))
            print("Total due: %.1f\n" % (rad[2]))

def insert_product(conn):
    peker = conn.cursor()

    navn = input('Product name: \n >>')
    pris = input('Price: \n >>')
    kategori = input('Category: \n >>')
    beskrivelse = input('Description: \n >>')
    print('\n')

    peker.execute("\
	SELECT cid \
	    FROM ws.categories \
	WHERE name = %(kategori)s;", {"kategori": kategori})

    rader = peker.fetchall()
    if rader == []:
        print("Category '%s' is not in system\n" % (kategori))
        return
    katId = rader[0][0]

    peker.execute("INSERT INTO ws.products(name, price, cid, description)\
        VALUES (%(navn)s, %(pris)s, %(kategori)s, %(beskrivelse)s);",
        {"navn": navn, "pris": pris, "kategori": katId, "beskrivelse": beskrivelse})

    conn.commit()

    print("New product %s inserted." % (navn) +"\n")


if __name__ == "__main__":
    administrator()
