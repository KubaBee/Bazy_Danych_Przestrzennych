# Rozwiązanie do zestawu z cwiczen 8 12.12.2021



import datetime
import os
import urllib.request
import zipfile
import psycopg2
import shutil
import smtplib
import ssl
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

timestamp = datetime.datetime.now().strftime("%m%d%Y")
log = open('main_'+timestamp, 'w')

# downloading file
try:
    url = 'https://home.agh.edu.pl/~wsarlej/Customers_Nov2021.zip'
    filehandle, _ = urllib.request.urlretrieve(url)
except Exception as e:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Downloading file - Filed\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Downloading filed - Success\n')

# extracting zip
try:
    with zipfile.ZipFile(filehandle, 'r') as file:
        password = 'agh'
        file.extract('Customers_Nov2021.csv', pwd=(bytes(password, 'utf-8')))
except Exception as e:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Extracting zip - Failed\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Extracting zip - Success\n')

# reading data form files
customers_new = open('Customers_Nov2021.csv', 'r')
customers_new_list = customers_new.readlines()
customers_new.close()
pob = len(customers_new_list) - 1

customers_old = open('Customers_old.csv', 'r')
customers_old_list = customers_old.readlines()
customers_old.close()

# validation
try:
    # clearing blank lines
    customers_new_list = [x for x in customers_new_list if x != "\n"]
    pob_clean = len(customers_new_list) - 1
    # checking for duplicates from old list
    for item in range(1, len(customers_old_list)):
        while customers_old_list[item] in customers_new_list:
            customers_new_list.remove(customers_old_list[item])
except Exception:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Validation - Fail\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Validation - Success\n')

pob_db = len(customers_new_list) -1 
pob_duplicates = pob_clean - pob_db

# saving fixed data to file
with open('Customers_Nov2021.csv', 'w+') as customers_new:
    customers_new.writelines(customers_new_list)

# DATABASE
password = os.environ['API_PASSWORD']
my_index = '401476'
conn = psycopg2.connect("dbname=customers user=postgres password=" + password)
cur = conn.cursor()

# creating db
try:
    create_table = "CREATE TABLE IF NOT EXISTS CUSTOMERS_" + my_index + """(
    id SERIAL PRIMARY KEY,
    first_name text,
    last_name text,
    email text,
    location GEOGRAPHY(POINT,4326))
    """
    cur.execute(create_table)
except (Exception, psycopg2.DatabaseError):
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Creating database - Fail\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Creating database - Success\n')

# inserting all values
try:
    for single in range(1, len(customers_new_list)):
        person = customers_new_list[single].split(',')
        inside = f"'{person[0]}', '{person[1]}', '{person[2]}', st_GeomFromText('POINT({float(person[4])} {float(person[3])})')"
        values = "INSERT INTO CUSTOMERS_" + my_index + \
                 "(first_name, last_name, email, location) VALUES(" + inside + ");"
        cur.execute(values)
except(Exception, psycopg2.DatabaseError):
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Inserting values - Fail\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Inserting values - Success\n')

# searching for best customers
try:
    best_customers = """
    SELECT first_name, last_name 
                INTO BEST_CUSTOMERS_401476
                FROM customers_401476 WHERE ST_DistanceSpheroid( 
                ST_SetSRID(location::geometry,0), ST_Point(-75.67329768604034,41.39988501005976),
                'SPHEROID["WGS 84",6378137,298.257223563]')/1000 < 50
    """
    cur.execute(best_customers)
except(Exception, psycopg2.DatabaseError):
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Searching for best customers - Fail\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Searching for best customers - Success\n')

# exporting to csv
try:
    export_csv = "COPY BEST_CUSTOMERS_401476 TO 'C:/Users/1kuba/OneDrive/Pulpit/Studia/Studia_s5/DBP/cw8/BEST_CUSTOMERS_401476.csv' DELIMITER ',' CSV HEADER;"
    cur.execute(export_csv)
    conn.commit()
except(Exception, psycopg2.DatabaseError) as e:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Exporting csv - Fail\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Exporting csv - Success\n')

# moving file
try:
    if not os.path.isdir('PROCESSED'):
        os.mkdir("C:/Users/1kuba/OneDrive/Pulpit/Studia/Studia_s5/DBP/cw8/PROCESSED")
    shutil.move("Customers_Nov2021.csv", "./PROCESSED/" + timestamp + "_Customers_Nov2021.csv")
except (Exception, shutil.Error) as e:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Moving file - Fail\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Moving file - Success\n')

# zipping csv with result
try:
    with zipfile.ZipFile('BEST_CUSTOMERS.zip', 'w') as zip_obj:
        zip_obj.write('BEST_CUSTOMERS_401476.csv')
    # getting file info
    last_modified = time.ctime(os.path.getmtime('BEST_CUSTOMERS_401476.csv'))
    with open('BEST_CUSTOMERS_401476.csv', 'r') as file:
        lines_len = len(file.readlines()) - 1
except Exception:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Zipping File - Fail\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Zipping File - Success\n')

# sending email
smtp_server = "smtp.gmail.com"
port = 587
password = 'testing4321'
context = ssl.create_default_context()
sender_email = "00thisistestemail00@gmail.com"

try:
    server = smtplib.SMTP(smtp_server, port)
    server.starttls(context=context)
    server.login(sender_email, password)

    # 1st mail
    m1 = MIMEMultipart()
    text = f""""
    liczba wierszy w pliku pobranym z internetu: {pob}\n
    liczba poprawnych wierszy (poczyszczeniu): {pob_clean}\n
    liczba duplikatów w pliku wejściowym: {pob_duplicates}\n
    ilość danych załadowanych do tabeli: {pob_db}
    """
    m1['Subject'] = 'First Email'
    m1.attach(MIMEText(text, 'plain'))
    text = m1.as_string()

    server.sendmail(sender_email, "1kubaape1@gmail.com", text)
except Exception as e:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Sending first email - Fail\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Sending emails - Success\n')

try:
    # 2nd mail
    m2 = MIMEMultipart()
    m2['Subject'] = "Email with file"
    text2 = f"""
    Data ostatniej modyfikacji: {last_modified}\n
    Ilosc wierszy: {lines_len}\n
    """
    m2.attach(MIMEText(text2, 'plain'))

    with open('BEST_CUSTOMERS.zip', 'rb') as attachment:
        at = MIMEBase('application', 'octet-stream')
        at.set_payload(attachment.read())
    encoders.encode_base64(at)
    at.add_header("Content-Disposition", f"attachment; filename=BEST_CUSTOMERS.zip")
    m2.attach(at)
    text = m2.as_string()
    server.sendmail(sender_email, "1kubaape1@gmail.com", text)
except Exception:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Sending second email - Fail\n')
else:
    log.write(f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")} - Sending second email - Success\n')
finally:
    server.quit()

log.close()
