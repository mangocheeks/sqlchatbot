import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

#Page setup
st.set_page_config(page_title="Dashboard", page_icon="😀", layout='wide')
st.write("# Sales Dashboard")

st.markdown("""---""")
st.write("#### Walmart Total Sales and Simple Moving Average\n")


#kPI sales dashboard mockup
def singlevaluegetter(query, db, col):
    output = pd.read_sql_query(query, db)
    df = pd.DataFrame(output)
    item = (df[col].to_list())[0]
    return str(item)

conn = create_engine("sqlite:///sales.db")
total_sales = singlevaluegetter('select round(total) as totalsale from (select sum(total) as total from walmart) a', conn, "totalsale")
total_invoices = singlevaluegetter('select count(*) as count from walmart', conn, "count")
avg_rating = singlevaluegetter('select round(avg(rating+0.0), 2) as avg from walmart', conn, 'avg')


col1, col2, col3 = st.columns(3)

with col1:
    st.header("$"+total_sales)
    st.write("Total Sales")

with col2:
    st.header(total_invoices)
    st.write("Total Invoices")

with col3:
    st.header(avg_rating+"⭐")
    st.write("Average Rating")


#SMA Line Graph
sma_query = 'SELECT Date, daily_revenue, AVG(daily_revenue) OVER (ORDER BY Date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as SMA FROM (select date, sum(total) as daily_revenue from walmart group by date) a'
SQL_Query = pd.read_sql_query(sma_query, conn)

sma_data = pd.DataFrame(SQL_Query, columns=["SMA","daily_revenue"])

#Get dates separately
dateq = 'Select distinct date from walmart'
datequery = pd.read_sql_query(dateq, conn, parse_dates=["Date"])
data_data=pd.DataFrame(datequery, columns=["Date"])
dates = data_data["Date"].tolist()

data = sma_data.assign(Dates=dates)

st.line_chart(data, x="Dates", y=["SMA", "daily_revenue"])
data_data['Date'] = data_data['Date'].astype(str)

##########################


#Adidas Bar Graph

retailquery2='''
select
    "Retailer",
    sum("Total Sales") as "Total Sales" 
from (
    select
    "Retailer",
    (REPLACE("Total Sales", ',', '')) as "Total Sales", 
    strftime( '%m-%Y', "Invoice Date") as "Date"
from adidas) a
group by "Retailer";'''

retailquery='''
select
    "Retailer",
    "Date",
    sum("Total Sales") as "Monthly Sales" 
from (
    select
    "Retailer",
    (REPLACE("Total Sales", ',', '')) as "Total Sales", 
    strftime( '%m-%Y', "Invoice Date") as "Date"
from adidas) a
group by "Retailer", "Date";
'''
st.markdown("""---""")
st.write("#### Adidas Retailer Statistics\n")

output =  pd.read_sql_query(retailquery, conn)
retaildf=pd.DataFrame(output, columns=["Retailer", "Monthly Sales", "Date"])
st.bar_chart(retaildf, x="Date", y="Monthly Sales", color="Retailer", stack=False)

output2 =  pd.read_sql_query(retailquery2, conn)
retaildf2=pd.DataFrame(output2, columns=["Retailer", "Total Sales"])
st.bar_chart(retaildf2, x="Retailer", y="Total Sales", color="Retailer", horizontal=True)

###################

#Zara Statistics
top10 = 'SELECT name, url, price, Sales_Volume FROM zara ORDER BY CAST(Sales_Volume AS INTEGER) DESC LIMIT 10'
terms = 'SELECT terms, count(terms) as termcount FROM zara group by terms limit 5'
zaraterms = pd.DataFrame(pd.read_sql_query(terms, conn), columns=["terms", "termcount"])
zaratop10 = pd.DataFrame(pd.read_sql_query(top10, conn), columns=["name", "Sales_Volume", "price"])

top10 = 'SELECT name, price FROM zara ORDER BY price DESC LIMIT 10'

top10price = 'SELECT price, price+0.0 as priced, name FROM zara order by priced desc limit 10'
zaratop101 = pd.DataFrame(pd.read_sql_query(top10price, conn), columns=["name", "price"])

st.markdown("""---""")
st.write("#### Zara Product Breakdown\n")

zcol1, zcol2, zcol3 = st.columns([1,1,2], gap ='small', vertical_alignment="top")

with zcol1:
    st.header("Top 10 Best Selling Products")
    st.write(zaratop10)

with zcol2:
    st.header("Top 10 Most Expensive Products")
    st.write(zaratop101)

with zcol3:
    st.header("Clothing composition")
    labels = zaraterms["terms"].tolist()
    sizes = zaraterms["termcount"].tolist()
    explode = (0,0,0,0,0) 
    fig1, ax1 = plt.subplots()
    
    fig1.patch.set_alpha(0)
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'color':"w"})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)


#Sidebar about information
sideb = st.sidebar
with sideb.expander("About Walmart Dataset"):
    st.write('''
        Records sales from three different branches of Walmart with columns such as Invoice ID, Branch, City, Customer type, Quantity, Total, Payment, Rating, etc.
    ''')
with sideb.expander("About Adidas Dataset"):
    st.write('''
        Describes sales of Adidas products with columns such as Retailer, Retailer ID, Invoice Date, Product, Units Sold, Total Sales, etc.
    ''')
with sideb.expander("About Zara Dataset"):
    st.write('''
        Lists sales of Zara products with fields like Product_ID, Product_Category, Sales_Volume, description, price, etc.
    ''')
