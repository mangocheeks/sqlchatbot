#taken from about page

graphexamples = [
    [
        ['''query: 'SELECT Date, daily_revenue, AVG(daily_revenue) OVER (ORDER BY Date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as SMA FROM (select date, sum(total) as daily_revenue from walmart group by date) a;'''],
        ['''question: Generate a line graph showing walmart's daily revenue plus its calculated simple moving average. Dates are on the x axis and sma and daily revenue are on the y axis.'''],
        ['''code:
    import streamlit as st
    import pandas as pd
    from sqlalchemy import create_engine

    conn = create_engine("sqlite:///sales.db")
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
    ''']
    ],
    [
        ['''query: 
         select
                "Retailer",
                sum("Total Sales") as "Monthly Sales" 
            from (
                select
                "Retailer",
                (REPLACE("Total Sales", ',', '')) as "Total Sales", 
                strftime( '%m-%Y', "Invoice Date") as "Date"
            from adidas) a
            group by "Retailer";
         '''],
        ['''question: Create a horizontal bar graph showing the total sales for adidas by retailer. X axis is Retailer and y is monthly sales'''],
        ['''code: 
         retailquery2='
            select
                "Retailer",
                sum("Total Sales") as "Monthly Sales" 
            from (
                select
                "Retailer",
                (REPLACE("Total Sales", ',', '')) as "Total Sales", 
                strftime( '%m-%Y', "Invoice Date") as "Date"
            from adidas) a
            group by "Retailer";'

        output2 =  pd.read_sql_query(retailquery2, conn)
        retaildf2=pd.DataFrame(output2, columns=["Retailer", "Monthly Sales"])
        st.bar_chart(retaildf2, x="Retailer", y="Monthly Sales", color="Retailer", horizontal=True)
         ''']
    ],
    [
        ['''query:
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

         '''],
        ['''question: Get a bar graph of the sales of each retailer by month for adidas. x axis should be dates, y axis should be sales
         '''],
        ['''code:
         
         retailquery='
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
group by "Retailer", "Date";'
         
         output =  pd.read_sql_query(retailquery, conn)
retaildf=pd.DataFrame(output, columns=["Retailer", "Monthly Sales", "Date"])
st.bar_chart(retaildf, x="Date", y="Monthly Sales", color="Retailer", stack=False)

''']
    ],
    [
        ['''query: SELECT terms, count(terms) as termcount FROM zara group by terms limit 5;'''],
        ['''question: Draw a matplotlib pie chart showing the percent composition of different types of clothing in zara'''],
        ['''code:
         import matplotlib.pyplot as plt

         terms = 'SELECT terms, count(terms) as termcount FROM zara group by terms limit 5;'
         zaraterms = pd.DataFrame(pd.read_sql_query(terms, conn), columns=["terms", "termcount"])
        labels = zaraterms["terms"].tolist()
    sizes = zaraterms["termcount"].tolist()
    explode = (0,0,0,0,0) 
    fig1, ax1 = plt.subplots()
    
    fig1.patch.set_alpha(0)
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'color':"w"})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)
         ''']
    ]
]
examples = [
    {
        "input": "Select top 10 most expensive items from Zara",
        "query": 
        '''SELECT
            price+0.0 as float_price,
            name
        FROM zara
        ORDER BY float_price DESC
        LIMIT 10;''',
    },
    
    {
        "input": "Find the total revenue by month for Walmart",
        "query": 
        '''SELECT
            date,
            sum(total) as daily_revenue
        FROM walmart
        GROUP BY date;''',
    },

    {
        "input": "Find the total sales for Zara's basic puffer jacket",
        "query": 
        '''SELECT name,
        ((Sales_Volume+0)*(price+0.0)) as Sales
        FROM zara
        where name = "BASIC PUFFER JACKET";''',
    },

    {
        "input": "Find the sum of all total sales for Adidas",
        "query": 
        '''SELECT
            SUM(REPLACE("Total Sales", ',', '')) AS "Combined_Total_Sales"
        FROM adidas;''',
    },
    
    {
        "input": "Show combined total sales for adidas by retailer",
        "query": 
        '''SELECT
            "Retailer",
            SUM(REPLACE("Total Sales", ',', '')) AS "Combined_Total_Sales"
        FROM adidas
        GROUP BY "Retailer";''',
    },
]



#multiple chat models, non destructive, iterative

def format_examples(examples):
    formatted_str = ""
    for example in examples:
        formatted_str += f"User input: {example['input']}\n"
        formatted_str += f"SQL query: {example['query']}\n\n"
    return formatted_str.strip()

#table info is copied from chatai output
#in the future possibly create funcitono to extract table info on its own
#this way uses less queries, save tokens

table_info = '''
CREATE TABLE adidas (
	"Retailer" TEXT, 
	"Retailer ID" TEXT, 
	"Invoice Date" TEXT, 
	"Region" TEXT, 
	"State" TEXT, 
	"City" TEXT, 
	"Product" TEXT, 
	"Price per Unit" TEXT, 
	"Units Sold" TEXT, 
	"Total Sales" TEXT, 
	"Operating Profit" TEXT, 
	"Sales Method" TEXT
)

/*
3 rows from adidas table:
Retailer	Retailer ID	Invoice Date	Region	State	City	Product	Price per Unit	Units Sold	Total Sales	Operating Profit	Sales Method
Walmart	1128299	6/17/2021	Southeast	Florida	Orlando	Women's Apparel	$103.00 	218	2,245	$1,257 	Online
West Gear	1128299	7/16/2021	South	Louisiana	New Orleans	Women's Apparel	$103.00 	163	1,679	$806 	Online
Sports Direct	1197831	8/25/2021	South	Alabama	Birmingham	Men's Street Footwear	$10.00 	700	7,000	$3,150 	Outlet
*/


CREATE TABLE walmart (
	"Invoice ID" TEXT, 
	"Branch" TEXT, 
	"City" TEXT, 
	"Customer type" TEXT, 
	"Gender" TEXT, 
	"Product line" TEXT, 
	"Unit price" TEXT, 
	"Quantity" TEXT, 
	"Tax 5%" TEXT, 
	"Total" TEXT, 
	"Date" TEXT, 
	"Time" TEXT, 
	"Payment" TEXT, 
	cogs TEXT, 
	"gross margin percentage" TEXT, 
	"gross income" TEXT, 
	"Rating" TEXT
)

/*
3 rows from walmart table:
Invoice ID	Branch	City	Customer type	Gender	Product line	Unit price	Quantity	Tax 5%	Total	Date	Time	Payment	cogs	gross margin percentage	gross income	Rating
750-67-8428	A	Yangon	Member	Female	Health and beauty	74.69	7	26.1415	548.9715	2019-01-05	13:08:00	Ewallet	522.83	4.761904762	26.1415	9.1
226-31-3081	C	Naypyitaw	Normal	Female	Electronic accessories	15.28	5	3.82	80.22	2019-03-08	10:29:00	Cash	76.4	4.761904762	3.82	9.6
631-41-3108	A	Yangon	Normal	Male	Home and lifestyle	46.33	7	16.2155	340.5255	2019-03-03	13:23:00	Credit card	324.31	4.761904762	16.2155	7.4
*/


CREATE TABLE zara (
	"Product_ID" TEXT, 
	"Product_Position" TEXT, 
	"Promotion" TEXT, 
	"Product_Category" TEXT, 
	"Seasonal" TEXT, 
	"Sales_Volume" TEXT, 
	brand TEXT, 
	url TEXT, 
	sku TEXT, 
	name TEXT, 
	description TEXT, 
	price TEXT, 
	currency TEXT, 
	scraped_at TEXT, 
	terms TEXT, 
	section TEXT
)

/*
3 rows from zara table:
Product_ID	Product_Position	Promotion	Product_Category	Seasonal	Sales_Volume	brand	url	sku	name	description	price	currency	scraped_at	terms	section
Product_ID	Product_Position	Promotion	Product_Category	Seasonal	Sales_Volume	brand	url	sku	name	description	price	currency	scraped_at	terms	section
185102	Aisle	No	Clothing	No	2823	Zara	https://www.zara.com/us/en/basic-puffer-jacket-p06985450.html	272145190-250-2	BASIC PUFFER JACKET	Puffer jacket made of tear-resistant ripstop fabric. High collar and adjustable long sleeves with ad	19.99	USD	2024-02-19T08:50:05.654618	jackets	MAN
188771	Aisle	No	Clothing	No	654	Zara	https://www.zara.com/us/en/tuxedo-jacket-p08896675.html	324052738-800-46	TUXEDO JACKET	Straight fit blazer. Pointed lapel collar and long sleeves with buttoned cuffs. Welt pockets at hip 	169.0	USD	2024-02-19T08:50:06.590930	jackets	MAN
*/

'''